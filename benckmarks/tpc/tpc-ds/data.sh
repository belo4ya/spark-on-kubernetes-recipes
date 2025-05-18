#!/usr/bin/env bash

DGEN_EXEC=${DGEN_EXEC:-dsdgen}
OUT_DIR=${OUT_DIR:-./data}
SF=${SF:-100}
PARALLEL=${PARALLEL:-8}
PART=${PART:-$PARALLEL}

out_dir="$OUT_DIR/sf$SF/chunks"
mkdir -p "$out_dir"

for i in $(seq 1 "$PART"); do
  $DGEN_EXEC -quiet Y -force -distributions "$TPCDS_DISTRIBUTIONS" -scale "$SF" -dir "$out_dir" -parallel "$PARALLEL" -child "$i" &
done

wait

pushd "$out_dir" > /dev/null || exit 1

tables=( \
  call_center catalog_page catalog_returns catalog_sales customer \
  customer_address customer_demographics date_dim dbgen_version \
  household_demographics income_band inventory item promotion reason \
  ship_mode store store_returns store_sales time_dim warehouse \
  web_page web_returns web_sales web_site \
)

for tbl in "${tables[@]}"; do
  mkdir -p "$tbl"
  for f in "${tbl}"_*_*.dat; do
    [ -e "$f" ] && mv "$f" "$tbl/"
  done
  echo "$tbl done"
done

popd > /dev/null || exit 1
