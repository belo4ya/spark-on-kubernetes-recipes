#!/usr/bin/env bash
set -euo pipefail
set -x

MODE=${MODE:-"chunks"} # csv, parquet
BENCH=${BENCH:-"tpc-h"} # tpc-ds
SRC_PATH=${SRC_PATH:-./tpc-h/data/sf1/chuncks}
DST_PATH=${DST_PATH:-s3a://spark-benchmark/tpc-h/data/sf1/csv}

SPARK_CLUSTER=${SPARK_CLUSTER:-"local-cluster[6,4,9216]"}
SPARK_EXECUTOR_MEM=${SPARK_EXECUTOR_MEM:-7680m}
SPARK_EXECUTOR_MEM_OVERHEAD=${SPARK_EXECUTOR_MEM_OVERHEAD:-1536m}

to_parquet() {
  export AWS_JAVA_V1_DISABLE_DEPRECATION_ANNOUNCEMENT=true
  /opt/spark/bin/spark-submit \
    --master "$SPARK_CLUSTER" \
    --files ./log4j.properties \
    --conf spark.executor.memory="$SPARK_EXECUTOR_MEM" \
    --conf spark.executor.memoryOverhead="$SPARK_EXECUTOR_MEM_OVERHEAD" \
    --conf spark.ui.showConsoleProgress=false \
    --conf spark.driver.extraJavaOptions="-Dlog4j.configuration=log4j.properties" \
    --conf spark.executor.extraJavaOptions="-Dlog4j.configuration=log4j.properties" \
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
    --conf spark.sql.legacy.charVarcharAsString=true \
    ./to_parquet.py \
    --src="$SRC_PATH" \
    --dst="$DST_PATH" \
    --bench="$BENCH" \
    --mode="$MODE"
}

to_parquet
