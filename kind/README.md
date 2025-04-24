```shell
kind create cluster --config config.yaml && kubectx kind-v31

helm upgrade --install vmoperator vm/victoria-metrics-operator \
    -n vm --create-namespace \
    -f vm/values.yaml

helm upgrade --install kubeflow-spark-operator spark-operator/spark-operator \
    -n kubeflow-spark-operator --create-namespace \
    -f operator/kubeflow/values.yaml
    
helm upgrade --install apache-spark-kubernetes-operator ./operator/apache/spark-kubernetes-operator/build-tools/helm/spark-kubernetes-operator/ \
    -n apache-spark-operator --create-namespace \
    -f operator/apache/values.yaml

helm upgrade --install virtual-nodes utils/virtual-nodes --qps 5
```
