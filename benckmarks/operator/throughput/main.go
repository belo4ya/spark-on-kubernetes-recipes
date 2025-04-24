package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"html/template"
	"log"
	"os"
	"sync"
	"time"

	"github.com/samber/lo"
	"github.com/sourcegraph/conc/pool"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/serializer/yaml"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/kubernetes"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/tools/cache"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/manager/signals"
	"sigs.k8s.io/controller-runtime/pkg/source"
)

var (
	scheme = runtime.NewScheme()

	flagTmpl = flag.String("tmpl", "", "")
	flagN    = flag.Int("n", 1, "")
	flagP    = flag.Int("p", 2, "")
)

func init() {
	flag.Parse()
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(corev1.AddToScheme(scheme))
}

func main() {
	ctx := signals.SetupSignalHandler()
	k8sClient := lo.Must(client.New(ctrl.GetConfigOrDie(), client.Options{Scheme: scheme}))

	// Determine namespace from template
	namespace := extractNamespace()

	var wg sync.WaitGroup
	wg.Add(2)

	// Start generator
	go func() {
		defer wg.Done()
		err := generateLoad(ctx, k8sClient)
		if err != nil {
			log.Fatalf("Error generating load: %v", err)
		}
	}()

	// Start monitoring
	go func() {
		defer wg.Done()
		err := monitorBenchmark(ctx, k8sClient, namespace, *flagN)
		if err != nil {
			log.Fatalf("Error monitoring benchmark: %v", err)
		}
	}()

	wg.Wait()
	log.Println("Benchmark complete")
}

// extractNamespace extracts the namespace from the template file for monitoring
func extractNamespace() string {
	data := lo.Must(os.ReadFile(*flagTmpl))
	obj := &unstructured.Unstructured{}
	decoder := yaml.NewDecodingSerializer(unstructured.UnstructuredJSONScheme)
	_, _, err := decoder.Decode(data, nil, obj)
	if err != nil {
		log.Fatalf("Failed to decode template to extract namespace: %v", err)
	}
	namespace := obj.GetNamespace()
	if namespace == "" {
		namespace = "default"
	}
	return namespace
}

// generateLoad creates resources based on the template
func generateLoad(ctx context.Context, k8sClient client.Client) error {
	p := pool.New().
		WithContext(ctx).
		WithMaxGoroutines(*flagP).
		WithCancelOnError().
		WithFirstError()

	data := lo.Must(os.ReadFile(*flagTmpl))
	tmpl := template.Must(template.New("").Parse(string(data)))

	for i := range *flagN {
		p.Go(func(ctx context.Context) error {
			var buf bytes.Buffer
			lo.Must0(tmpl.Execute(&buf, map[string]any{"Index": fmt.Sprintf("%04d", i)}))

			obj := &unstructured.Unstructured{}
			decoder := yaml.NewDecodingSerializer(unstructured.UnstructuredJSONScheme)
			lo.Must2(decoder.Decode(buf.Bytes(), nil, obj))

			lo.Must0(k8sClient.Create(ctx, obj))

			log.Printf("[%04d/%04d] created resource %s/%s\n", i+1, *flagN, obj.GetNamespace(), obj.GetName())
			return nil
		})
	}

	return p.Wait()
}

// monitorBenchmark watches for pod creations and records metrics
func monitorBenchmark(ctx context.Context, k8sClient client.Client, namespace string, expectedCount int) error {
	startTime := time.Now()
	resultFile := fmt.Sprintf("benchmark-results-%s.csv", time.Now().Format("20060102-150405"))

	f, err := os.Create(resultFile)
	if err != nil {
		return fmt.Errorf("failed to create results file: %w", err)
	}
	defer f.Close()

	// Write header
	_, err = f.WriteString("time,pods_count\n")
	if err != nil {
		return fmt.Errorf("failed to write header: %w", err)
	}

	podCount := 0
	var mu sync.Mutex

	informers_ := informers.NewSharedInformerFactory(kubernetes.NewForConfigOrDie(ctrl.GetConfigOrDie()), 10*time.Hour)
	informers_.Core().V1().Pods().Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj any) {

		},
		UpdateFunc: nil,
		DeleteFunc: nil,
	})

	// Setup informer
	informer, err := k8sClient.Scheme().New(corev1.SchemeGroupVersion.WithKind("Pod"))
	if err != nil {
		return fmt.Errorf("failed to create pod object: %w", err)
	}

	podWatcher, err := source.NewKindWithCache(informer.(*corev1.Pod), cache.WatchFunc(func(options cache.ListOptions) (runtime.Object, error) {
		podList := &corev1.PodList{}
		err := k8sClient.List(ctx, podList, &client.ListOptions{Namespace: namespace})
		return podList, err
	}))
	if err != nil {
		return fmt.Errorf("failed to create pod watcher: %w", err)
	}

	// Watch for pod creations
	stop := make(chan struct{})
	defer close(stop)

	go func() {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()

		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.Tick():
				mu.Lock()
				elapsed := time.Since(startTime).Seconds()
				_, err := f.WriteString(fmt.Sprintf("%.2f,%d\n", elapsed, podCount))
				if err != nil {
					log.Printf("Error writing to results file: %v", err)
				}
				mu.Unlock()

				if podCount >= expectedCount {
					log.Printf("Benchmark complete: %d/%d pods created", podCount, expectedCount)
					return
				}
			}
		}
	}()

	// Setup handler for pod events
	_, err = podWatcher.Start(ctx, cache.ResourceEventHandlerFuncs{
		AddFunc: func(obj interface{}) {
			pod := obj.(*corev1.Pod)
			mu.Lock()
			podCount++
			log.Printf("Pod created: %s (%d/%d)", pod.Name, podCount, expectedCount)
			mu.Unlock()
		},
	})
	if err != nil {
		return fmt.Errorf("failed to start pod watcher: %w", err)
	}

	// Wait until all pods are created or context is canceled
	<-ctx.Done()
	return nil
}
