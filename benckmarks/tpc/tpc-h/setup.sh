#!/usr/bin/env bash

alias aws-s3="aws s3 --no-verify-ssl"

aws-s3 cp s3://spark-benchmark/tpc-h/tpc-h-tool-v3.0.1.zip tpc-h-tool-v3.0.1.zip
unzip tpc-h-tool-v3.0.1.zip

cd tpc-h-tool-v3.0.1.zip/dbgen || exit 1
make -f makefile.suite CC=gcc MACHINE=LINUX WORKLOAD=TPCH DATABASE=ORACLE
