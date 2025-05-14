#!/usr/bin/env bash

MODE=${MODE:-"tbl"}
SRC_PATH=${SRC_PATH:-./tpc-h/data/sf1/tbl}
DST_PATH=${DST_PATH:-spark-benchmark/tpc-h/data/sf1/tbl}
PARQUET_DST_PATH=${PARQUET_DST_PATH:-spark-benchmark/tpc-h/data/sf1/parquet}

upload_tbl() {
  echo "Uploading TBL files to S3..."
  aws --endpoint-url="$AWS_ENDPOINT_URL" --no-verify-ssl s3 cp --recursive "$SRC_PATH/" "s3://$DST_PATH/"
}

to_parquet() {
  echo "Converting TBL files to Parquet format..."
  /opt/spark/bin/spark-submit \
    --master "local-cluster[3,1,2048]" \
    --conf spark.hadoop.fs.s3a.access.key="$AWS_ACCESS_KEY_ID" \
    --conf spark.hadoop.fs.s3a.secret.key="$AWS_SECRET_ACCESS_KEY" \
    --conf spark.hadoop.fs.s3a.endpoint="$AWS_ENDPOINT_URL" \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
    ./to_parquet.py \
    --src="$SRC_PATH" \
    --dst="s3a://$PARQUET_DST_PATH"
}

case $MODE in
  "tbl")
    upload_tbl
    ;;
  "parquet")
    to_parquet
    ;;
  "tbl-parquet")
    upload_tbl
    to_parquet
    ;;
  *)
    echo "Invalid mode: $MODE"
    echo "Supported modes: tbl, parquet, tbl-parquet"
    exit 1
    ;;
esac
