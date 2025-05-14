```shell
docker run --rm -it --user=root -v ./:/opt/tpch_data spark:3.5.5-java17 bash

export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_ENDPOINT_URL=https://s3.ru-7.storage.selcloud.ru

aws s3 --no-verify-ssl ls --recursive s3://spark-benchmark

# TPC-H
aws s3 --no-verify-ssl cp ./tpc-h/tpc-h-tool-v3.0.1.zip s3://spark-benchmark/tpc-h/tpc-h-tool-v3.0.1.zip

aws s3 --no-verify-ssl cp ./tpc-h/data/ s3://spark-benchmark/tpc-h/data/ --recursive

# TPC-DS
aws s3 --no-verify-ssl cp ./tpc-ds/tpc-ds-tool-v4.0.0.zip s3://spark-benchmark/tpc-ds/tpc-ds-tool-v4.0.0.zip
```
