package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/apimachinery/pkg/types"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/manager/signals"
)

var (
	scheme = runtime.NewScheme()

	flagOperator  = flag.String("operator", "apache", "apache or kubeflow")
	flagNamespace = flag.String("namespace", "spark-jobs", "")
	flagLabel     = flag.String("label", "spark-jobs", "")
)

func init() {
	flag.Parse()
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(corev1.AddToScheme(scheme))
}

func main() {
	ctx := signals.SetupSignalHandler()

	k8sClient, err := client.New(ctrl.GetConfigOrDie(), client.Options{Scheme: scheme})
	if err != nil {
		log.Fatal(fmt.Errorf("client.New: %w", err))
	}

	jobs := &unstructured.UnstructuredList{}
	jobs.SetGroupVersionKind(GVKFromOperator(*flagOperator))
	if err := k8sClient.List(ctx, jobs, client.InNamespace(*flagNamespace), client.HasLabels{*flagLabel}); err != nil {
		log.Fatal(fmt.Errorf("k8sClient.List: %w", err))
	}
	log.Printf("found %d SparkApplications", len(jobs.Items))

	pods := &corev1.PodList{}
	if err := k8sClient.List(ctx, pods, client.InNamespace(*flagNamespace), client.HasLabels{*flagLabel}); err != nil {
		log.Fatal(fmt.Errorf("k8sClient.List: %w", err))
	}
	log.Printf("found %d pods", len(pods.Items))

	jobsCreatedMap := make(map[types.UID]metav1.Time, len(jobs.Items))
	for _, job := range jobs.Items {
		jobsCreatedMap[job.GetUID()] = job.GetCreationTimestamp()
	}

	stats := make([]Stats, 0, len(pods.Items))
	for _, pod := range pods.Items {
		stats = append(stats, Stats{
			JobCreated: jobsCreatedMap[pod.OwnerReferences[0].UID].Time,
			PodCreated: pod.CreationTimestamp.Time,
		})
	}

	path := fmt.Sprintf("results_%s_%s.csv", *flagOperator, time.Now().Format("20060102-150405"))
	if err := StatsToCSV(stats, path); err != nil {
		log.Fatal(fmt.Errorf("StatsToCSV: %w", err))
	}
}

type Stats struct {
	JobCreated time.Time
	PodCreated time.Time
}

func StatsToCSV(stats []Stats, path string) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("os.Create: %w", err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)

	if _, err = f.WriteString("start,end\n"); err != nil {
		return fmt.Errorf("f.WriteString: %w", err)
	}
	for _, row := range stats {
		if _, err = f.WriteString(fmt.Sprintf("%d,%d\n", row.JobCreated.Unix(), row.PodCreated.Unix())); err != nil {
			return fmt.Errorf("f.WriteString: %w", err)
		}
	}

	return nil
}

func GVKFromOperator(operator string) schema.GroupVersionKind {
	if operator == "apache" {
		return schema.GroupVersionKind{
			Group:   "spark.apache.org",
			Version: "v1alpha1",
			Kind:    "SparkApplicationList",
		}
	}
	return schema.GroupVersionKind{
		Group:   "sparkoperator.k8s.io",
		Version: "v1beta2",
		Kind:    "SparkApplicationList",
	}
}
