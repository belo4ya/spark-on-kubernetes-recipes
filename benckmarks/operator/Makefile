# kubeflow or apache
OPERATOR ?= apache

.PHONY: up
up: clean create-kind
	make wait
	make -j 3 create-kwok create-monitoring create-operator

.PHONY: clean
clean:
	kind delete clusters v31

.PHONY: create-kind
create-kind:
	kind create cluster --config kind.yaml && kubectx kind-v31

.PHONY: create-kwok
create-kwok:
	kustomize build kwok/ | kubectl create -f -

.PHONY: create-monitoring
create-monitoring:
	helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
      -n monitoring --create-namespace \
      --set alertmanager.enabled=false \
      --set kubeStateMetrics.enabled=false

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
	kubectl create ns spark-jobs
	helm install kubeflow-spark-operator spark-operator/spark-operator --version=2.1.1 \
		-n spark-operator --create-namespace \
		-f kubeflow/values.yaml

.PHONY: create-operator-apache
create-operator-apache:
	helm install spark-kubernetes-operator spark-kubernetes-operator/spark-kubernetes-operator --version=0.1.0 \
		-n spark-operator --create-namespace \
		-f apache/values.yaml

.PHONY: wait
wait:
	-for i in $$(seq 1 60); do \
		kubectl wait -A --for=condition=Ready=True pod --all \
			--timeout=10s >/dev/null 2>&1 && break; \
	done
	sleep 1
