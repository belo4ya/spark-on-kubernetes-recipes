import argparse
import typing as t

from pyspark.sql import SparkSession

TPC_H_EXT = "tbl"
TPC_H_TABLES = [
    "customer",
    "lineitem",
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


def to_parquet(spark: SparkSession, src: str, dst: str, benchmark: t.Literal["tpc-h", "tpc-ds"]) -> None:
    if benchmark == "tpc-h":
        tables = TPC_H_TABLES
        ext = TPC_H_EXT
    elif benchmark == "tpc-ds":
        tables = TPC_DS_TABLES
        ext = TPC_DS_EXT
    else:
        raise ValueError(f"unknown benchmark '{benchmark}'")

    for table in tables:
        df = spark.read.csv(f"{src}/{table}.{ext}", sep="|", inferSchema=True)
        if df.columns and df.columns[-1].startswith("_c"):
            df = df.drop(df.columns[-1])
        df.write.mode("overwrite").parquet(f"{dst}/{table}")


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
    args = parser.parse_args()

    spark = SparkSession.builder.appName("Parquet Conversion").getOrCreate()

    to_parquet(spark, args.src, args.dst, args.bench)

    spark.stop()


if __name__ == "__main__":
    main()
