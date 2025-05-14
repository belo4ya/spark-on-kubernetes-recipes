#!/usr/bin/env bash

DBGEN_EXEC=${DBGEN_EXEC:-dbgen}
OUT_DIR=${OUT_DIR:-./data}
SF=${SF:-1}

for tbl in c L n O P r s S; do
  $DBGEN_EXEC -q -f -b "$TPCH_DISTS_DSS" -s "$SF" -T $tbl &
done
wait

out_dir="$OUT_DIR/sf$SF/tbl"
mkdir -p "$out_dir" && mv *.tbl "$out_dir"
