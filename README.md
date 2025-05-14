# Spark on Kubernetes Recipes

> 🚧 UNDER CONSTRUCTION 🚧

**Тема:** Modern, Scalable, Feature-Rich and Cost-Effective Spark on Kubernetes
**Аннотация:**

- Сложный простой Spark на Kubernetes

- Выбор оператора: популярный [kubeflow/spark-operator](https://github.com/kubeflow/spark-operator) vs
  новый [apache/spark-kubernetes-operator](https://github.com/apache/spark-kubernetes-operator)
    - побенчмаркал throughput (проблема бинарника с JVM) и эффективность использования ресурсов
    - сравнил функциональность

- Выбор планировщика:
  default-scheduler, [volcano](https://github.com/volcano-sh/volcano), [yunikorn](https://yunikorn.apache.org/), [kueue](https://github.com/kubernetes-sigs/kueue) (
  default-scheduler+[scheduler-plugins](https://github.com/kubernetes-sigs/scheduler-plugins/tree/master))
    - сравнил функциональность
    - побенчмаркал эффективную утилизацию
    - побенчмаркал throughput

- Работа с Shuffle/Spill: сравнение SSD как hostPath, onDemand PVC, Remote Shuffle Service
    - производительность, время восстановления + совместимость с DRA, масштабирование, экономическая эффективность
    - побенчмаркал разные
      RSS: [apache/celeborn](https://github.com/apache/celeborn), [apache/uniffle](https://github.com/apache/uniffle), [zuston/riffle](https://github.com/zuston/riffle)

- Spark Connect:
    - альтернатива [apache/livy](https://github.com/apache/incubator-livy) и классическим реализациям Spark + Jupyter
      Notebook
    - реализация авторизации

- Акселераторы:
    - Spark+GPU: сборка spark-rapids, бенчмарки
    - Opensource-альтернативы Databricks Photon:
      побенчмаркал [kwai/blaze](https://github.com/kwai/blaze), [apache/datafusion-comet](https://github.com/apache/datafusion-comet), [apache/incubator-gluten](https://github.com/apache/incubator-gluten) + [facebookincubator/velox](https://github.com/facebookincubator/velox/)

- Kubernetes прочее:
    - спотовые узлы, Cluster Autoscaler (+ DRA)
    - кеширование образов
    - мониторинг, spark-history-server, JMX exporters

- Прочее:
    - IaC: Terraform + Yandex Cloud
    - сравнение с облегченными Spark-кластерами Yandex Cloud DataProc

*Работа больше обзорно-исследовательская* ~~и не такая идеальная, как эта аннотация 😅~~
