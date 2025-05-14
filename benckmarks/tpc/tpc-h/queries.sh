#!/usr/bin/env bash

cd dbgen || exit 1
make -f makefile.suite CC=gcc MACHINE=LINUX WORKLOAD=TPCH DATABASE=ORACLE

export DSS_QUERY=queries

SF=100
for q in {1..22}; do
  ./qgen -a -d -N -b ./dists.dss -s $SF "$q" | tail -n +5 > "../../queries/$q.sql"
done
