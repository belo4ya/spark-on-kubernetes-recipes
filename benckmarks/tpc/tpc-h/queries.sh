#!/usr/bin/env bash

QGEN_EXEC=${QGEN_EXEC:-qgen}
OUT_DIR=${OUT_DIR:-./queries}
SF=${SF:-100}

for q in {1..22}; do
  $QGEN_EXEC -a -d -N -b "$TPCH_DISTS_DSS" -s "$SF" "$q" | tail -n +5 > "$OUT_DIR/$q.sql"
done
