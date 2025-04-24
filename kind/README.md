```shell
kind create cluster --config config.yaml && kubectx kind-v31

helm install spark-operator spark-operator/spark-operator \
    --namespace spark-operator \
    --create-namespace \
    -f operator/kubeflow/values.yaml
    
helm upgrade --install virtual-nodes utils/virtual-nodes --qps 5
```
