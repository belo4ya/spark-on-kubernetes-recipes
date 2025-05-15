#!/usr/bin/env bash

DGEN_EXEC=${DGEN_EXEC:-dsdgen}
OUT_DIR=${OUT_DIR:-./data}
SF=${SF:-1}
PARALLEL=${PARALLEL:-8}

out_dir="$OUT_DIR/sf$SF/csv"
mkdir -p "$out_dir"

for i in $(seq 1 "$PARALLEL"); do
  $DGEN_EXEC -force -distributions "$TPCDS_DISTRIBUTIONS" -scale "$SF" -dir "$out_dir" -parallel "$PARALLEL" -child "$i" &
done

wait

# combine chunks
pushd "$out_dir" > /dev/null || exit 1

tables=$(ls *_*_[0-9]*.dat 2>/dev/null | sed -E 's/_[0-9]+_[0-9]+\.dat$//' | sort -u)
for tbl in $tables; do
  cat "${tbl}"_[0-9]*_[0-9]*.dat > "${tbl}.dat"
  rm -f "${tbl}"_[0-9]*_[0-9]*.dat
done

popd > /dev/null || exit 1
