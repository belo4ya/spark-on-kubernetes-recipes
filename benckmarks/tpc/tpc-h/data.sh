#!/usr/bin/env bash

cd dbgen || exit 1
make -f makefile.suite CC=gcc MACHINE=LINUX WORKLOAD=TPCH DATABASE=ORACLE

# --------- DATA
SF=1
for tbl in c L n O P r s S; do
  ./dbgen -q -f -s $SF -T $tbl  &
done
wait

data_dir="../../data/sf$SF/tbl"
mkdir -p $data_dir && mv *.tbl $data_dir

# --------- SPARK PARQUET
cd ../

SF=1
spark-submit \
  --master "local[3,1,2048]" \
  --conf spark.hadoop.fs.s3a.access.key="$AWS_ACCESS_KEY_ID" \
  --conf spark.hadoop.fs.s3a.secret.key="$AWS_SECRET_ACCESS_KEY" \
  --conf spark.hadoop.fs.s3a.endpoint="$AWS_ENDPOINT_URL" \
  /opt/tpch/to_parquet.py \
  --src s3a://spark-benchmark/tpc-h/data/sf$SF/tbl \
  --dst s3a://spark-benchmark/tpc-h/data/sf$SF/parquet
