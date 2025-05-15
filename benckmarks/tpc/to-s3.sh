#!/usr/bin/env bash

set -x

MODE=${MODE:-"csv"}
BENCHMARK=${BENCHMARK:-"tpc-h"} # tpc-ds
SRC_PATH=${SRC_PATH:-./tpc-h/data/sf1/csv}
DST_PATH=${DST_PATH:-spark-benchmark/tpc-h/data/sf1/csv}
PARQUET_DST_PATH=${PARQUET_DST_PATH:-spark-benchmark/tpc-h/data/sf1/parquet}

upload_csv() {
  echo "Uploading CSV files to S3..."
  aws --endpoint-url="$AWS_ENDPOINT_URL" --no-verify-ssl s3 cp --recursive "$SRC_PATH/" "s3://$DST_PATH/"
}

to_parquet() {
  echo "Converting CSV files to Parquet format..."
  /opt/spark/bin/spark-submit \
    --master "local-cluster[12,1,2048]" \
    --conf spark.executor.memory=1280m \
    --conf spark.executor.memoryOverhead=512m \
    --conf spark.hadoop.fs.s3a.access.key="$AWS_ACCESS_KEY_ID" \
    --conf spark.hadoop.fs.s3a.secret.key="$AWS_SECRET_ACCESS_KEY" \
    --conf spark.hadoop.fs.s3a.endpoint="$AWS_ENDPOINT_URL" \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
    --conf spark.hadoop.fs.s3a.committer.name=magic \
    --conf spark.hadoop.fs.s3a.committer.magic.enabled=true \
    --conf spark.sql.sources.commitProtocolClass=org.apache.spark.internal.io.cloud.PathOutputCommitProtocol \
    --conf spark.sql.parquet.output.committer.class=org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter \
    --conf spark.hadoop.parquet.enable.summary-metadata=false \
    --conf spark.sql.parquet.mergeSchema=false \
    --conf spark.sql.parquet.filterPushdown=true \
    --conf spark.sql.hive.metastorePartitionPruning=true \
    --conf spark.sql.parquet.compression.codec=zstd \
    --conf parquet.compression.codec.zstd.level=19 \
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
