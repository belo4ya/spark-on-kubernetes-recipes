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
	"golang.org/x/sync/errgroup"
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
)

var (
	scheme = runtime.NewScheme()

	flagTmpl    = flag.String("tmpl", "", "")
	flagN       = flag.Int("n", 1, "")
	flagP       = flag.Int("p", 2, "")
	flagTimeout = flag.Int("timeout", 30, "")
)

func init() {
	flag.Parse()
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(corev1.AddToScheme(scheme))
}

func main() {
	ctx, cancel := context.WithTimeout(signals.SetupSignalHandler(), time.Duration(*flagTimeout)*time.Second)
	defer cancel()

	k8sClient := lo.Must(client.New(ctrl.GetConfigOrDie(), client.Options{Scheme: scheme}))

	data := lo.Must(os.ReadFile(*flagTmpl))
	tmpl := template.Must(template.New("").Parse(string(data)))

	start := make(chan struct{})
	defer close(start)

	eg, ctx := errgroup.WithContext(ctx)
	eg.Go(func() error {
		err := MonitorBenchmark(ctx, tmpl, start)
		if err != nil {
			return fmt.Errorf("MonitorBenchmark: %w", err)
		}
		return nil
	})
	eg.Go(func() error {
		err := GenerateLoad(ctx, k8sClient, tmpl, start)
		if err != nil {
			return fmt.Errorf("GenerateLoad: %w", err)
		}
		return nil
	})

	if err := eg.Wait(); err != nil {
		log.Fatal(err)
	}
}

// GenerateLoad creates resources based on the template
func GenerateLoad(ctx context.Context, k8sClient client.Client, tmpl *template.Template, start <-chan struct{}) error {
	<-start
	p := pool.New().
		WithContext(ctx).
		WithMaxGoroutines(*flagP).
		WithCancelOnError().
		WithFirstError()

	for i := range *flagN {
		p.Go(func(ctx context.Context) error {
			obj := lo.Must(ObjectFormTemplate(tmpl, i))
			lo.Must0(k8sClient.Create(ctx, obj))
			log.Printf("[%04d/%04d] created resource %s/%s\n", i+1, *flagN, obj.GetNamespace(), obj.GetName())
			return nil
		})
	}

	return p.Wait()
}

// MonitorBenchmark watches for pod creations and records metrics
func MonitorBenchmark(ctx context.Context, tmpl *template.Template, start chan<- struct{}) error {
	var startTime time.Time

	type Row struct {
		secs int
		pods int
	}
	rows := []Row{{secs: 0, pods: 0}}
	var mu sync.Mutex

	stop := make(chan struct{})
	defer close(stop)

	obj := lo.Must(ObjectFormTemplate(tmpl, 1))
	informers_ := informers.NewSharedInformerFactoryWithOptions(
		kubernetes.NewForConfigOrDie(ctrl.GetConfigOrDie()),
		10*time.Hour,
		informers.WithNamespace(obj.GetNamespace()),
	)
	lo.Must(informers_.Core().V1().Pods().Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: func(_ any) {
			mu.Lock()
			pods := rows[len(rows)-1].pods + 1
			rows = append(rows, Row{secs: int(time.Since(startTime).Seconds()), pods: pods})
			fmt.Println(pods)
			if pods >= *flagN {
				stop <- struct{}{}
			}
			mu.Unlock()
		},
	}))

	informers_.Start(ctx.Done())
	startTime = time.Now().UTC()
	start <- struct{}{}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-stop:
	}

	f, err := os.Create(fmt.Sprintf("throughput-result-%s.csv", startTime.Format("20060102-150405")))
	if err != nil {
		return fmt.Errorf("os.Create: %w", err)
	}
	defer f.Close()

	if _, err = f.WriteString("secs,pods\n"); err != nil {
		return fmt.Errorf("f.WriteString: %w", err)
	}
	for _, row := range rows {
		if _, err = f.WriteString(fmt.Sprintf("%d,%d\n", row.secs, row.pods)); err != nil {
			return fmt.Errorf("f.WriteString: %w", err)
		}
	}

	return nil
}

func ObjectFormTemplate(tmpl *template.Template, i int) (client.Object, error) {
	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, map[string]any{"Index": fmt.Sprintf("%04d", i)}); err != nil {
		return nil, fmt.Errorf("tmpl.Execute: %v", err)
	}
	obj := &unstructured.Unstructured{}
	decoder := yaml.NewDecodingSerializer(unstructured.UnstructuredJSONScheme)
	if _, _, err := decoder.Decode(buf.Bytes(), nil, obj); err != nil {
		return nil, fmt.Errorf("decoder.Decode: %w", err)
	}
	return obj, nil
}
