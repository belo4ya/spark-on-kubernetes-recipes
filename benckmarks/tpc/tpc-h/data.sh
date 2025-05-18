#!/usr/bin/env bash

DGEN_EXEC=${DGEN_EXEC:-dbgen}
OUT_DIR=${OUT_DIR:-./data}
SF=${SF:-1}
PARALLEL=${PARALLEL:-8}

out_dir="$OUT_DIR/sf$SF/chunks"
mkdir -p "$out_dir"
pushd "$out_dir" > /dev/null || exit 1

for i in $(seq 1 "$PARALLEL"); do
  $DGEN_EXEC -q -f -b "$TPCH_DISTS_DSS" -s "$SF" -C "$PARALLEL" -S "$i" &
done

wait

for tbl in customer orders lineitem part partsupp supplier nation region; do
  mkdir -p "$tbl"
  for f in "$tbl".tbl*; do
    [ -e "$f" ] && mv "$f" "$tbl/"
  done
  echo "$tbl done"
done

popd > /dev/null || exit 1
