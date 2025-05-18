#!/usr/bin/env bash

set -x

MODE=${MODE:-"csv"}
BENCHMARK=${BENCHMARK:-"tpc-h"} # tpc-ds
SRC_PATH=${SRC_PATH:-./tpc-h/data/sf1/csv}
DST_PATH=${DST_PATH:-spark-benchmark/tpc-h/data/sf1/csv}
PARQUET_DST_PATH=${PARQUET_DST_PATH:-spark-benchmark/tpc-h/data/sf1/parquet}

SPARK_CLUSTER=${SPARK_CLUSTER:-"local-cluster[6,4,9216]"}
SPARK_EXECUTOR_MEM=${SPARK_EXECUTOR_MEM:-7680m}
SPARK_EXECUTOR_MEM_OVERHEAD=${SPARK_EXECUTOR_MEM_OVERHEAD:-1536m}

upload_csv() {
  echo "Uploading CSV files to S3..."
  aws --endpoint-url="$AWS_ENDPOINT_URL" --no-verify-ssl s3 cp --recursive "$SRC_PATH/" "s3://$DST_PATH/"
}

to_parquet() {
  echo "Converting CSV files to Parquet format..."
  /opt/spark/bin/spark-submit \
    --master "$SPARK_CLUSTER" \
    --conf spark.executor.memory="$SPARK_EXECUTOR_MEM" \
    --conf spark.executor.memoryOverhead="$SPARK_EXECUTOR_MEM_OVERHEAD" \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
    --conf spark.hadoop.fs.s3a.access.key="$AWS_ACCESS_KEY_ID" \
    --conf spark.hadoop.fs.s3a.secret.key="$AWS_SECRET_ACCESS_KEY" \
    --conf spark.hadoop.fs.s3a.endpoint="$AWS_ENDPOINT_URL" \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.mapreduce.outputcommitter.factory.scheme.s3a=org.apache.hadoop.fs.s3a.commit.S3ACommitterFactory \
    --conf spark.hadoop.fs.s3a.committer.name=magic \
    --conf spark.hadoop.fs.s3a.committer.magic.enabled=true \
    --conf spark.hadoop.fs.s3a.committer.abort.pending.uploads=true \
    --conf spark.hadoop.fs.s3a.create.performance=true \
    --conf spark.sql.sources.commitProtocolClass=org.apache.spark.internal.io.cloud.PathOutputCommitProtocol \
    --conf spark.sql.parquet.output.committer.class=org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter \
    --conf spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version=2 \
    --conf spark.hadoop.mapreduce.fileoutputcommitter.cleanup-failures.ignored=true \
    --conf spark.hadoop.parquet.hadoop.vectored.io.enabled=true \
    --conf spark.hadoop.fs.s3a.fast.upload=true \
    --conf spark.hadoop.fs.s3a.fast.upload.buffer=disk \
    --conf spark.hadoop.fs.s3a.multipart.size=128m \
    --conf spark.hadoop.fs.s3a.multipart.threshold=512m \
    --conf spark.hadoop.parquet.enable.summary-metadata=false \
    --conf spark.sql.parquet.mergeSchema=false \
    --conf spark.sql.parquet.filterPushdown=true \
    --conf spark.sql.hive.metastorePartitionPruning=true \
    --conf spark.hadoop.fs.s3a.experimental.input.fadvise=random \
    --conf spark.sql.parquet.compression.codec=zstd \
    --conf spark.hadoop.parquet.compression.codec.zstd.level=9 \
    ./to_parquet.py \
    --src="$SRC_PATH" \
    --dst="s3a://$PARQUET_DST_PATH" \
    --bench="$BENCHMARK"
}

case $MODE in
  "csv")
    upload_csv
    ;;
  "parquet")
    to_parquet
    ;;
  "csv-parquet")
    upload_csv
    to_parquet
    ;;
  *)
    echo "Invalid mode: $MODE"
    echo "Supported modes: csv, parquet, csv-parquet"
    exit 1
    ;;
esac
