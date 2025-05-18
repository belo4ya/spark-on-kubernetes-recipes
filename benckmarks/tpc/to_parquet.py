import argparse
import glob
import os
import re
import shutil
import typing as t

from pyspark.sql import SparkSession, DataFrame

BenchmarkT = t.Literal["tpc-h", "tpc-ds"]

TPC_H_EXT = "tbl"
TPC_H_TABLES = [
    "lineitem",
    "customer",
    "nation",
    "orders",
    "part",
    "partsupp",
    "region",
    "supplier",
]

TPC_DS_EXT = "dat"
TPC_DS_TABLES = [
    "call_center",
    "catalog_page",
    "catalog_returns",
    "catalog_sales",
    "customer",
    "customer_address",
    "customer_demographics",
    "date_dim",
    "dbgen_version",
    "household_demographics",
    "income_band",
    "inventory",
    "item",
    "promotion",
    "reason",
    "ship_mode",
    "store",
    "store_returns",
    "store_sales",
    "time_dim",
    "warehouse",
    "web_page",
    "web_returns",
    "web_sales",
    "web_site",
]


def get_tables_and_ext(benchmark: BenchmarkT) -> tuple[list[str], str]:
    if benchmark == "tpc-h":
        return TPC_H_TABLES, TPC_H_EXT
    elif benchmark == "tpc-ds":
        return TPC_DS_TABLES, TPC_DS_EXT
    else:
        raise ValueError(f"unknown benchmark '{benchmark}'")


def get_chunk_key(benchmark: BenchmarkT) -> t.Callable[[str], int]:
    if benchmark == "tpc-ds":
        ext = TPC_DS_EXT

        def chunk_key(fname: str) -> int:
            m = re.search(f"\w+_(\d+)_\d+\.{ext}", fname)
            return int(m.group(1)) if m else -1

    else:
        ext = TPC_H_EXT

        def chunk_key(fname: str) -> int:
            m = re.search(f"\w+\.{ext}.(\d+)", fname)
            return int(m.group(1)) if m else -1

    return chunk_key


def read_chunks_in_order(spark: SparkSession, src_dir: str, benchmark: BenchmarkT, sep: str = "|") -> DataFrame:
    hadoop_conf = spark._jsc.hadoopConfiguration()
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(hadoop_conf)
    path = spark._jvm.org.apache.hadoop.fs.Path(src_dir)
    status = fs.listStatus(path)

    files = [f.getPath().toString() for f in status if f.isFile()]
    files_sorted = sorted(files, key=get_chunk_key(benchmark))

    df_all = None
    for fpath in files_sorted:
        df_chunk = spark.read.csv(
            fpath,
            sep=sep,
            header=False,
            ignoreLeadingWhiteSpace=False,
            ignoreTrailingWhiteSpace=False,
        )
        df_all = df_chunk if df_all is None else df_all.union(df_chunk)

    return df_all


def chunks_to_csv(spark: SparkSession, src: str, dst: str, benchmark: BenchmarkT) -> None:
    tables, ext = get_tables_and_ext(benchmark)

    # tpc-h: customer.tbl.1, customer.tbl.2, customer.tbl.3, ...
    # tpc-ds: customer_1_1000.dat, customer_2_1000.dat, customer_3_1000.dat, ...

    for table in tables:
        tmp_dir = os.path.join(dst, "tmp", table)

        df = read_chunks_in_order(spark, f"{src}/{table}", benchmark=benchmark, sep="|")
        df.coalesce(1).write.mode("overwrite").csv(
            tmp_dir,
            sep="|",
            header=False,
            ignoreLeadingWhiteSpace=False,
            ignoreTrailingWhiteSpace=False,
        )

        src_file = glob.glob(os.path.join(tmp_dir, "*.csv"))[0]

        shutil.move(src_file, os.path.join(dst, f"{table}.{ext}"))
        shutil.rmtree(tmp_dir, ignore_errors=True)
        shutil.rmtree(f"{src}/{table}", ignore_errors=True)

        print(f"[chunks_to_csv] {table}")

    shutil.rmtree(os.path.join(dst, "tmp"), ignore_errors=True)


def csv_to_csv_or_parquet(
    spark: SparkSession,
    src: str,
    dst: str,
    benchmark: BenchmarkT,
    mode: t.Literal["csv", "parquet"],
) -> None:
    tables, ext = get_tables_and_ext(benchmark)

    for table in tables:
        df = spark.read.csv(f"{src}/{table}.{ext}", sep="|", header=False, inferSchema=True)
        df = df.drop(df.columns[-1])
        if mode == "csv":
            df.write.mode("overwrite").csv(f"{dst}/{table}", sep="|", header=False)
        elif mode == "parquet":
            df.write.mode("overwrite").parquet(f"{dst}/{table}")
        else:
            raise ValueError(f"unknown mode '{mode}'")

        print(f"[csv_to_csv_or_parquet] {table}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert CSV on S3 to Parquet")
    parser.add_argument(
        "--src",
        required=True,
        help="S3 source path, e.g. s3a://bucket/sf10/csv",
    )
    parser.add_argument(
        "--dst",
        required=True,
        help="S3 destination path, e.g. s3a://bucket/sf10/parquet",
    )
    parser.add_argument(
        "--bench",
        required=True,
        choices=["tpc-h", "tpc-ds"],
        help="Benchmark type, e.g. tpc-h or tpc-ds",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["chunks", "csv", "parquet"],
        help="Mode, e.g. chunks, csv or parquet",
    )
    args = parser.parse_args()

    spark = SparkSession.builder.appName("Parquet Conversion").getOrCreate()

    if args.mode == "chunks":
        chunks_to_csv(spark, args.src, args.dst, args.bench)
    else:
        csv_to_csv_or_parquet(spark, args.src, args.dst, args.bench, args.mode)

    spark.stop()


if __name__ == "__main__":
    main()
