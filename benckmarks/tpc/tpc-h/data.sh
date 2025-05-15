#!/usr/bin/env bash

DGEN_EXEC=${DGEN_EXEC:-dbgen}
OUT_DIR=${OUT_DIR:-./data}
SF=${SF:-1}
PARALLEL=${PARALLEL:-8}

# all tables except lineitem.tbl
for tbl in c n O P r s S; do
  $DGEN_EXEC -q -f -b "$TPCH_DISTS_DSS" -s "$SF" -T $tbl &
done

# lineitem.tbl
for i in $(seq 1 "$PARALLEL"); do
  $DGEN_EXEC -q -f -b "$TPCH_DISTS_DSS" -s "$SF" -C "$PARALLEL" -S "$i" -T L &
done

wait

rm -f lineitem.tbl
for chunk in lineitem.tbl.*; do
  cat "$chunk" >> lineitem.tbl
  rm -f "$chunk"
done

out_dir="$OUT_DIR/sf$SF/csv"
mkdir -p "$out_dir" && mv *.tbl "$out_dir"
