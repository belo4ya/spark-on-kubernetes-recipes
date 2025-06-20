# kubeflow or apache
OPERATOR ?= apache

.PHONY: up
up: clean create-kind
	make wait
	make -j 3 create-kwok create-monitoring create-operator
	make create-fake-nodes

.PHONY: bench
bench:
	cd benchmark \
		&& kube-burner init -c ${OPERATOR}.kube-burner.throughput.yaml --uuid=${OPERATOR} \
		&& go run main.go -operator=${OPERATOR} -namespace=spark-jobs -label=spark-jobs \
		&& mmv "results_${OPERATOR}_*.csv" "results_${OPERATOR}_throughput_#1.csv"
	make clean-spark-jobs
	cd benchmark \
		&& kube-burner init -c ${OPERATOR}.kube-burner.latency.yaml --uuid=${OPERATOR} \
		&& go run main.go -operator=${OPERATOR} -namespace=spark-jobs -label=spark-jobs \
		&& mmv "results_${OPERATOR}_*.csv" "results_${OPERATOR}_latency_#1.csv"
	make clean-spark-jobs

.PHONY: clean
clean:
	kind delete clusters v31

.PHONY: create-kind
create-kind:
	kind create cluster --config kind.yaml && kubectx kind-v31
	kubectl patch daemonset -n kube-system kindnet --type=json -p '[{"op":"remove","path":"/spec/template/spec/containers/0/resources"}]'
	kubectl patch daemonset -n kube-system kube-proxy --type=json -p '[{"op":"add","path":"/spec/template/spec/affinity","value":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"type","operator":"NotIn","values":["kwok"]}]}]}}}}]'

.PHONY: create-kwok
create-kwok:
	kustomize build kwok/ | kubectl create -f -

.PHONY: create-monitoring
create-monitoring:
	kustomize build kube-prometheus-stack/ | kubectl create -f - || true
	helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack --version=72.5.0 \
      -n monitoring --create-namespace \
      -f kube-prometheus-stack/values.yaml
	kubectl patch daemonset -n monitoring kube-prometheus-stack-prometheus-node-exporter --type=json -p '[{"op":"add","path":"/spec/template/spec/affinity","value":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"type","operator":"NotIn","values":["kwok"]}]}]}}}}]'


.PHONY: create-operator
create-operator:
ifeq ($(OPERATOR), kubeflow)
	make create-operator-kubeflow
else ifeq ($(OPERATOR), apache)
	make create-operator-apache
else
	@echo "Error: OPERATOR must be set to 'kubeflow' or 'apache'"
	@echo "Example: make create-operator OPERATOR=kubeflow"
	@exit 1
endif

.PHONY: create-operator-kubeflow
create-operator-kubeflow:
	kubectl create ns spark-jobs || true
	helm upgrade --install kubeflow-spark-operator spark-operator/spark-operator --version=2.1.1 \
		-n spark-operator --create-namespace \
		-f kubeflow/values.yaml

.PHONY: create-operator-apache
create-operator-apache:
	kubectl create ns spark-jobs || true
	helm upgrade --install spark-kubernetes-operator spark-kubernetes-operator/spark-kubernetes-operator --version=1.0.0 \
		-n spark-operator --create-namespace \
		-f apache/values.yaml

.PHONY: create-fake-nodes
create-fake-nodes:
	helm upgrade --install fake-nodes kwok/fake-nodes --qps 5

.PHONY: clean-spark-jobs
clean-spark-jobs:
ifeq ($(OPERATOR), kubeflow)
	kubectl delete sparkapplications.sparkoperator.k8s.io --all -n spark-jobs
else ifeq ($(OPERATOR), apache)
	kubectl delete sparkapplications.spark.apache.org --all -n spark-jobs
else
	@echo "Error: OPERATOR must be set to 'kubeflow' or 'apache'"
	@echo "Example: make create-operator OPERATOR=kubeflow"
	@exit 1
endif

.PHONY: wait
wait:
	-for i in $$(seq 1 60); do \
		kubectl wait -A --for=condition=Ready=True pod --all \
			--timeout=10s >/dev/null 2>&1 && break; \
	done
	sleep 1

.PHONY: test
test:
	mmv "results_kubeflow_*.csv" "results_kubeflow_latency_#1.csv"
