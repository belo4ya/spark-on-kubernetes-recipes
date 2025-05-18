# Benchmarks. TPC-H, TPC-DS

```shell
export AWS_SECRET_ACCESS_KEY=
docker build --build-arg=AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -t belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0 .
docker buildx build --platform=linux/amd64,linux/arm64 --build-arg=AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -t belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0 .

docker push belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0
```

```shell
docker run --rm -it -v ./../:/opt/tpc-benchmark/spark-on-kubernetes-recipes/benckmarks belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0

docker run --rm -it belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0

docker run -it -v ./spark-on-kubernetes-recipes:/opt/tpc-benchmark/spark-on-kubernetes-recipes --name spark-tpc-benchmark-tools belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0
```

```shell
git clone https://github.com/belo4ya/spark-on-kubernetes-recipes.git
docker run -it -v ./spark-on-kubernetes-recipes:/opt/tpc-benchmark/spark-on-kubernetes-recipes --name spark-tpc-benchmark-tools belo4ya/spark-tpc-benchmark-tools:tpc-h-v3.0.1-tpc-ds-v4.0.0
cd spark-on-kubernetes-recipes/benckmarks/tpc/
```

## TPC-H

```shell
cd tpc-h

# 1Gi
SF=1 PARALLEL=10 ./data.sh
# 10Gi
SF=10 PARALLEL=32 ./data.sh
# 100Gi
SF=100 PARALLEL=32 ./data.sh
# 300Gi
SF=300 PARALLEL=32 ./data.sh
# 1Ti
SF=1000 PARALLEL=32 ./data.sh
```

```shell
export BENCH=tpc-h
# local
export SPARK_CLUSTER='local-cluster[4,2,2048]'
export SPARK_EXECUTOR_MEM='1536m'
export SPARK_EXECUTOR_MEM_OVERHEAD='512m'
# 32 CPU, 64 Gi
export SPARK_CLUSTER='local-cluster[8,4,6144]'
export SPARK_EXECUTOR_MEM='4864m'
export SPARK_EXECUTOR_MEM_OVERHEAD='1280m'
# 24 CPU, 64 Gi
export SPARK_CLUSTER='local-cluster[6,4,8192]'
export SPARK_EXECUTOR_MEM='6912m'
export SPARK_EXECUTOR_MEM_OVERHEAD='1280m'

# 1Gi
MODE=chunks SRC_PATH=./tpc-h/data/sf1/chunks DST_PATH=./tpc-h/data/sf1/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-h/data/sf1/csv DST_PATH=s3a://spark-benchmark/tpc-h/data/sf1/parquet ./to-s3.sh

# 10Gi
MODE=chunks SRC_PATH=./tpc-h/data/sf10/chunks DST_PATH=./tpc-h/data/sf10/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-h/data/sf10/csv DST_PATH=s3a://spark-benchmark/tpc-h/data/sf10/parquet ./to-s3.sh

# 100Gi
MODE=chunks SRC_PATH=./tpc-h/data/sf100/chunks DST_PATH=./tpc-h/data/sf100/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-h/data/sf100/csv DST_PATH=s3a://spark-benchmark/tpc-h/data/sf100/parquet ./to-s3.sh

# 300Gi
MODE=chunks SRC_PATH=./tpc-h/data/sf300/chunks DST_PATH=./tpc-h/data/sf300/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-h/data/sf300/csv DST_PATH=s3a://spark-benchmark/tpc-h/data/sf300/parquet ./to-s3.sh

# 1Ti
MODE=chunks SRC_PATH=./tpc-h/data/sf1000/chunks DST_PATH=./tpc-h/data/sf1000/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-h/data/sf1000/csv DST_PATH=s3a://spark-benchmark/tpc-h/data/sf1000/parquet ./to-s3.sh
```

## TPC-DS

```shell
cd tpc-ds

# 1Gi
SF=100 PARALLEL=200 PART=2 ./data.sh && mv ./data/sf100 ./data/sf1
# 10Gi
SF=100 PARALLEL=200 PART=20 ./data.sh && mv ./data/sf100 ./data/sf10
# 100Gi
SF=100 PARALLEL=32 ./data.sh
# 300Gi
SF=300 PARALLEL=32 ./data.sh
# 1Ti
SF=1000 PARALLEL=32 ./data.sh
```

```shell
export BENCH=tpc-ds
# local
export SPARK_CLUSTER='local-cluster[4,2,2048]'
export SPARK_EXECUTOR_MEM='1536m'
export SPARK_EXECUTOR_MEM_OVERHEAD='512m'
# 32 CPU, 64 Gi
export SPARK_CLUSTER='local-cluster[8,4,6144]'
export SPARK_EXECUTOR_MEM='4864m'
export SPARK_EXECUTOR_MEM_OVERHEAD='1280m'
# 24 CPU, 64 Gi
export SPARK_CLUSTER='local-cluster[6,4,8192]'
export SPARK_EXECUTOR_MEM='6912m'
export SPARK_EXECUTOR_MEM_OVERHEAD='1280m'

# 1Gi
MODE=chunks SRC_PATH=./tpc-ds/data/sf1/chunks DST_PATH=./tpc-ds/data/sf1/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-ds/data/sf1/csv DST_PATH=s3a://spark-benchmark/tpc-ds/data/sf1/parquet ./to-s3.sh

# 10Gi
MODE=chunks SRC_PATH=./tpc-ds/data/sf10/chunks DST_PATH=./tpc-ds/data/sf10/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-ds/data/sf10/csv DST_PATH=s3a://spark-benchmark/tpc-ds/data/sf10/parquet ./to-s3.sh

# 100Gi
MODE=chunks SRC_PATH=./tpc-ds/data/sf100/chunks DST_PATH=./tpc-ds/data/sf100/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-ds/data/sf100/csv DST_PATH=s3a://spark-benchmark/tpc-ds/data/sf100/parquet ./to-s3.sh

# 300Gi
MODE=chunks SRC_PATH=./tpc-ds/data/sf300/chunks DST_PATH=./tpc-ds/data/sf300/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-ds/data/sf300/csv DST_PATH=s3a://spark-benchmark/tpc-ds/data/sf300/parquet ./to-s3.sh

# 1Ti
MODE=chunks SRC_PATH=./tpc-ds/data/sf1000/chunks DST_PATH=./tpc-ds/data/sf1000/csv ./to-s3.sh \
  && MODE=parquet SRC_PATH=./tpc-ds/data/sf1000/csv DST_PATH=s3a://spark-benchmark/tpc-ds/data/sf1000/parquet ./to-s3.sh
```
