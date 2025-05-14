import argparse

from pyspark.sql import SparkSession

TPC_H_TABLES = ["customer", "lineitem", "nation", "orders", "part", "partsupp", "region", "supplier"]
TPC_DS_TABLES = []


def to_parquet(spark: SparkSession, src: str, dst: str) -> None:
    for table in TPC_H_TABLES:
        df = spark.read.csv(f"{src}/{table}.tbl", sep="|", inferSchema=True)
        if df.columns and df.columns[-1].startswith("_c"):
            df = df.drop(df.columns[-1])
        df.write.mode("overwrite").parquet(f"{dst}/{table}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert CSV on S3 to Parquet")
    parser.add_argument("--src", required=True, help="S3 source path, e.g. s3a://bucket/sf10/tbl")
    parser.add_argument("--dst", required=True, help="S3 destination path, e.g. s3a://bucket/sf10/parquet")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("Parquet Conversion").getOrCreate()

    to_parquet(spark, args.src, args.dst)

    spark.stop()


if __name__ == "__main__":
    main()
