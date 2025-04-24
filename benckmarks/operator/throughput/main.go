package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"html/template"
	"log"
	"os"

	"github.com/samber/lo"
	"github.com/sourcegraph/conc/pool"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/serializer/yaml"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/manager/signals"
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
}

func main() {
	ctx := signals.SetupSignalHandler()
	k8sClient := lo.Must(client.New(ctrl.GetConfigOrDie(), client.Options{Scheme: scheme}))

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

			log.Printf("[%04d/%04d] created resource %s/%s\n", i, *flagN, obj.GetNamespace(), obj.GetName())
			return nil
		})
	}

	lo.Must0(p.Wait())
}
