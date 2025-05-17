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

cd spark-on-kubernetes-recipes/benckmarks/tpc/
```

## TPC-H

```shell
cd tpc-h

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
export BENCHMARK=tpc-h
export SPARK_WORKERS=30

# 10Gi
MODE=parquet SRC_PATH=./tpc-h/data/sf10/csv PARQUET_DST_PATH=spark-benchmark/tpc-h/data/sf10/parquet ./to-s3.sh
# 100Gi
MODE=parquet SRC_PATH=./tpc-h/data/sf100/csv PARQUET_DST_PATH=spark-benchmark/tpc-h/data/sf100/parquet ./to-s3.sh
# 300Gi
MODE=parquet SRC_PATH=./tpc-h/data/sf300/csv PARQUET_DST_PATH=spark-benchmark/tpc-h/data/sf300/parquet ./to-s3.sh
# 1Ti
MODE=parquet SRC_PATH=./tpc-h/data/sf1000/csv PARQUET_DST_PATH=spark-benchmark/tpc-h/data/sf1000/parquet ./to-s3.sh
```

## TPC-DS

```shell
cd tpc-ds

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
export BENCHMARK=tpc-ds
export SPARK_WORKERS=30

# 10Gi
MODE=parquet SRC_PATH=./tpc-ds/data/sf10/csv PARQUET_DST_PATH=spark-benchmark/tpc-ds/data/sf10/parquet ./to-s3.sh
# 100Gi
MODE=parquet SRC_PATH=./tpc-ds/data/sf100/csv PARQUET_DST_PATH=spark-benchmark/tpc-ds/data/sf100/parquet ./to-s3.sh
# 300Gi
MODE=parquet SRC_PATH=./tpc-ds/data/sf300/csv PARQUET_DST_PATH=spark-benchmark/tpc-ds/data/sf300/parquet ./to-s3.sh
# 1Ti
MODE=parquet SRC_PATH=./tpc-ds/data/sf1000/csv PARQUET_DST_PATH=spark-benchmark/tpc-ds/data/sf1000/parquet ./to-s3.sh
```
