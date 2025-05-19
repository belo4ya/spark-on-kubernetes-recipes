import argparse
import typing as t

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    IntegerType,
    LongType,
    DecimalType,
    CharType,
    VarcharType,
)

BenchmarkT = t.Literal["tpc-h", "tpc-ds"]

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
TPC_H_SCHEMAS = {
    "customer": StructType(
        [
            StructField("c_custkey", LongType(), False),
            StructField("c_name", StringType(), False),
            StructField("c_address", StringType(), False),
            StructField("c_nationkey", LongType(), False),
            StructField("c_phone", StringType(), False),
            StructField("c_acctbal", DecimalType(11, 2), False),
            StructField("c_mktsegment", StringType(), False),
            StructField("c_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "lineitem": StructType(
        [
            StructField("l_orderkey", LongType(), False),
            StructField("l_partkey", LongType(), False),
            StructField("l_suppkey", LongType(), False),
            StructField("l_linenumber", IntegerType(), False),
            StructField("l_quantity", DecimalType(11, 2), False),
            StructField("l_extendedprice", DecimalType(11, 2), False),
            StructField("l_discount", DecimalType(11, 2), False),
            StructField("l_tax", DecimalType(11, 2), False),
            StructField("l_returnflag", StringType(), False),
            StructField("l_linestatus", StringType(), False),
            StructField("l_shipdate", DateType(), False),
            StructField("l_commitdate", DateType(), False),
            StructField("l_receiptdate", DateType(), False),
            StructField("l_shipinstruct", StringType(), False),
            StructField("l_shipmode", StringType(), False),
            StructField("l_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "nation": StructType(
        [
            StructField("n_nationkey", LongType(), False),
            StructField("n_name", StringType(), False),
            StructField("n_regionkey", LongType(), False),
            StructField("n_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "orders": StructType(
        [
            StructField("o_orderkey", LongType(), False),
            StructField("o_custkey", LongType(), False),
            StructField("o_orderstatus", StringType(), False),
            StructField("o_totalprice", DecimalType(11, 2), False),
            StructField("o_orderdate", DateType(), False),
            StructField("o_orderpriority", StringType(), False),
            StructField("o_clerk", StringType(), False),
            StructField("o_shippriority", IntegerType(), False),
            StructField("o_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "part": StructType(
        [
            StructField("p_partkey", LongType(), False),
            StructField("p_name", StringType(), False),
            StructField("p_mfgr", StringType(), False),
            StructField("p_brand", StringType(), False),
            StructField("p_type", StringType(), False),
            StructField("p_size", IntegerType(), False),
            StructField("p_container", StringType(), False),
            StructField("p_retailprice", DecimalType(11, 2), False),
            StructField("p_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "partsupp": StructType(
        [
            StructField("ps_partkey", LongType(), False),
            StructField("ps_suppkey", LongType(), False),
            StructField("ps_availqty", IntegerType(), False),
            StructField("ps_supplycost", DecimalType(11, 2), False),
            StructField("ps_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "region": StructType(
        [
            StructField("r_regionkey", LongType(), False),
            StructField("r_name", StringType(), False),
            StructField("r_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
    "supplier": StructType(
        [
            StructField("s_suppkey", LongType(), False),
            StructField("s_name", StringType(), False),
            StructField("s_address", StringType(), False),
            StructField("s_nationkey", LongType(), False),
            StructField("s_phone", StringType(), False),
            StructField("s_acctbal", DecimalType(11, 2), False),
            StructField("s_comment", StringType(), False),
            StructField("ignore", StringType(), True),
        ]
    ),
}

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

IDENTIFIER_INT, IDENTIFIER_LONG = IntegerType(), LongType()
TPC_DS_SCHEMAS = {
    "call_center": StructType(
        [
            StructField("cc_call_center_sk", IDENTIFIER_INT, nullable=False),
            StructField("cc_call_center_id", CharType(16), nullable=False),
            StructField("cc_rec_start_date", DateType()),
            StructField("cc_rec_end_date", DateType()),
            StructField("cc_closed_date_sk", IDENTIFIER_INT),
            StructField("cc_open_date_sk", IDENTIFIER_INT),
            StructField("cc_name", VarcharType(50)),
            StructField("cc_class", VarcharType(50)),
            StructField("cc_employees", LongType()),
            StructField("cc_sq_ft", LongType()),
            StructField("cc_hours", CharType(20)),
            StructField("cc_manager", VarcharType(40)),
            StructField("cc_mkt_id", LongType()),
            StructField("cc_mkt_class", CharType(50)),
            StructField("cc_mkt_desc", VarcharType(100)),
            StructField("cc_market_manager", VarcharType(40)),
            StructField("cc_division", LongType()),
            StructField("cc_division_name", VarcharType(50)),
            StructField("cc_company", LongType()),
            StructField("cc_company_name", CharType(50)),
            StructField("cc_street_number", CharType(10)),
            StructField("cc_street_name", VarcharType(60)),
            StructField("cc_street_type", CharType(15)),
            StructField("cc_suite_number", CharType(10)),
            StructField("cc_city", VarcharType(60)),
            StructField("cc_county", VarcharType(30)),
            StructField("cc_state", CharType(2)),
            StructField("cc_zip", CharType(10)),
            StructField("cc_country", VarcharType(20)),
            StructField("cc_gmt_offset", DecimalType(5, 2)),
            StructField("cc_tax_percentage", DecimalType(5, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "catalog_page": StructType(
        [
            StructField("cp_catalog_page_sk", IDENTIFIER_INT, nullable=False),
            StructField("cp_catalog_page_id", CharType(16), nullable=False),
            StructField("cp_start_date_sk", IDENTIFIER_INT),
            StructField("cp_end_date_sk", IDENTIFIER_INT),
            StructField("cp_department", VarcharType(50)),
            StructField("cp_catalog_number", LongType()),
            StructField("cp_catalog_page_number", LongType()),
            StructField("cp_description", VarcharType(100)),
            StructField("cp_type", VarcharType(100)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "catalog_returns": StructType(
        [
            StructField("cr_returned_date_sk", IDENTIFIER_INT),
            StructField("cr_returned_time_sk", IDENTIFIER_INT),
            StructField("cr_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("cr_refunded_customer_sk", IDENTIFIER_INT),
            StructField("cr_refunded_cdemo_sk", IDENTIFIER_INT),
            StructField("cr_refunded_hdemo_sk", IDENTIFIER_INT),
            StructField("cr_refunded_addr_sk", IDENTIFIER_INT),
            StructField("cr_returning_customer_sk", IDENTIFIER_INT),
            StructField("cr_returning_cdemo_sk", IDENTIFIER_INT),
            StructField("cr_returning_hdemo_sk", IDENTIFIER_INT),
            StructField("cr_returning_addr_sk", IDENTIFIER_INT),
            StructField("cr_call_center_sk", IDENTIFIER_INT),
            StructField("cr_catalog_page_sk", IDENTIFIER_INT),
            StructField("cr_ship_mode_sk", IDENTIFIER_INT),
            StructField("cr_warehouse_sk", IDENTIFIER_INT),
            StructField("cr_reason_sk", IDENTIFIER_INT),
            StructField("cr_order_number", IDENTIFIER_INT, nullable=False),
            StructField("cr_return_quantity", LongType()),
            StructField("cr_return_amount", DecimalType(7, 2)),
            StructField("cr_return_tax", DecimalType(7, 2)),
            StructField("cr_return_amt_inc_tax", DecimalType(7, 2)),
            StructField("cr_fee", DecimalType(7, 2)),
            StructField("cr_return_ship_cost", DecimalType(7, 2)),
            StructField("cr_refunded_cash", DecimalType(7, 2)),
            StructField("cr_reversed_charge", DecimalType(7, 2)),
            StructField("cr_store_credit", DecimalType(7, 2)),
            StructField("cr_net_loss", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "catalog_sales": StructType(
        [
            StructField("cs_sold_date_sk", IDENTIFIER_INT),
            StructField("cs_sold_time_sk", IDENTIFIER_INT),
            StructField("cs_ship_date_sk", IDENTIFIER_INT),
            StructField("cs_bill_customer_sk", IDENTIFIER_INT),
            StructField("cs_bill_cdemo_sk", IDENTIFIER_INT),
            StructField("cs_bill_hdemo_sk", IDENTIFIER_INT),
            StructField("cs_bill_addr_sk", IDENTIFIER_INT),
            StructField("cs_ship_customer_sk", IDENTIFIER_INT),
            StructField("cs_ship_cdemo_sk", IDENTIFIER_INT),
            StructField("cs_ship_hdemo_sk", IDENTIFIER_INT),
            StructField("cs_ship_addr_sk", IDENTIFIER_INT),
            StructField("cs_call_center_sk", IDENTIFIER_INT),
            StructField("cs_catalog_page_sk", IDENTIFIER_INT),
            StructField("cs_ship_mode_sk", IDENTIFIER_INT),
            StructField("cs_warehouse_sk", IDENTIFIER_INT),
            StructField("cs_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("cs_promo_sk", IDENTIFIER_INT),
            StructField("cs_order_number", IDENTIFIER_INT, nullable=False),
            StructField("cs_quantity", LongType()),
            StructField("cs_wholesale_cost", DecimalType(7, 2)),
            StructField("cs_list_price", DecimalType(7, 2)),
            StructField("cs_sales_price", DecimalType(7, 2)),
            StructField("cs_ext_discount_amt", DecimalType(7, 2)),
            StructField("cs_ext_sales_price", DecimalType(7, 2)),
            StructField("cs_ext_wholesale_cost", DecimalType(7, 2)),
            StructField("cs_ext_list_price", DecimalType(7, 2)),
            StructField("cs_ext_tax", DecimalType(7, 2)),
            StructField("cs_coupon_amt", DecimalType(7, 2)),
            StructField("cs_ext_ship_cost", DecimalType(7, 2)),
            StructField("cs_net_paid", DecimalType(7, 2)),
            StructField("cs_net_paid_inc_tax", DecimalType(7, 2)),
            StructField("cs_net_paid_inc_ship", DecimalType(7, 2)),
            StructField("cs_net_paid_inc_ship_tax", DecimalType(7, 2)),
            StructField("cs_net_profit", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "customer": StructType(
        [
            StructField("c_customer_sk", IDENTIFIER_INT, nullable=False),
            StructField("c_customer_id", CharType(16), nullable=False),
            StructField("c_current_cdemo_sk", IDENTIFIER_INT),
            StructField("c_current_hdemo_sk", IDENTIFIER_INT),
            StructField("c_current_addr_sk", IDENTIFIER_INT),
            StructField("c_first_shipto_date_sk", IDENTIFIER_INT),
            StructField("c_first_sales_date_sk", IDENTIFIER_INT),
            StructField("c_salutation", CharType(10)),
            StructField("c_first_name", CharType(20)),
            StructField("c_last_name", CharType(30)),
            StructField("c_preferred_cust_flag", CharType(1)),
            StructField("c_birth_day", LongType()),
            StructField("c_birth_month", LongType()),
            StructField("c_birth_year", LongType()),
            StructField("c_birth_country", VarcharType(20)),
            StructField("c_login", CharType(13)),
            StructField("c_email_address", CharType(50)),
            StructField("c_last_review_date_sk", IDENTIFIER_INT),
            StructField("ignore", StringType(), True),
        ]
    ),
    "customer_address": StructType(
        [
            StructField("ca_address_sk", IDENTIFIER_INT, nullable=False),
            StructField("ca_address_id", CharType(16), nullable=False),
            StructField("ca_street_number", CharType(10)),
            StructField("ca_street_name", VarcharType(60)),
            StructField("ca_street_type", CharType(15)),
            StructField("ca_suite_number", CharType(10)),
            StructField("ca_city", VarcharType(60)),
            StructField("ca_county", VarcharType(30)),
            StructField("ca_state", CharType(2)),
            StructField("ca_zip", CharType(10)),
            StructField("ca_country", VarcharType(20)),
            StructField("ca_gmt_offset", DecimalType(5, 2)),
            StructField("ca_location_type", CharType(20)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "customer_demographics": StructType(
        [
            StructField("cd_demo_sk", IDENTIFIER_INT, nullable=False),
            StructField("cd_gender", CharType(1)),
            StructField("cd_marital_status", CharType(1)),
            StructField("cd_education_status", CharType(20)),
            StructField("cd_purchase_estimate", LongType()),
            StructField("cd_credit_rating", CharType(10)),
            StructField("cd_dep_count", LongType()),
            StructField("cd_dep_employed_count", LongType()),
            StructField("cd_dep_college_count", LongType()),
            StructField("ignore", StringType(), True),
        ]
    ),
    "date_dim": StructType(
        [
            StructField("d_date_sk", IDENTIFIER_INT, nullable=False),
            StructField("d_date_id", CharType(16), nullable=False),
            StructField("d_date", DateType()),
            StructField("d_month_seq", LongType()),
            StructField("d_week_seq", LongType()),
            StructField("d_quarter_seq", LongType()),
            StructField("d_year", LongType()),
            StructField("d_dow", LongType()),
            StructField("d_moy", LongType()),
            StructField("d_dom", LongType()),
            StructField("d_qoy", LongType()),
            StructField("d_fy_year", LongType()),
            StructField("d_fy_quarter_seq", LongType()),
            StructField("d_fy_week_seq", LongType()),
            StructField("d_day_name", CharType(9)),
            StructField("d_quarter_name", CharType(6)),
            StructField("d_holiday", CharType(1)),
            StructField("d_weekend", CharType(1)),
            StructField("d_following_holiday", CharType(1)),
            StructField("d_first_dom", LongType()),
            StructField("d_last_dom", LongType()),
            StructField("d_same_day_ly", LongType()),
            StructField("d_same_day_lq", LongType()),
            StructField("d_current_day", CharType(1)),
            StructField("d_current_week", CharType(1)),
            StructField("d_current_month", CharType(1)),
            StructField("d_current_quarter", CharType(1)),
            StructField("d_current_year", CharType(1)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "dbgen_version": StructType(
        [
            StructField("_c0", StringType(), True),
            StructField("_c1", DateType(), True),
            StructField("_c2", StringType(), True),
            StructField("_c3", StringType(), True),
            StructField("ignore", StringType(), True),
        ]
    ),
    "household_demographics": StructType(
        [
            StructField("hd_demo_sk", IDENTIFIER_INT, nullable=False),
            StructField("hd_income_band_sk", IDENTIFIER_INT),
            StructField("hd_buy_potential", CharType(15)),
            StructField("hd_dep_count", LongType()),
            StructField("hd_vehicle_count", LongType()),
            StructField("ignore", StringType(), True),
        ]
    ),
    "income_band": StructType(
        [
            StructField("ib_income_band_sk", IDENTIFIER_INT, nullable=False),
            StructField("ib_lower_bound", LongType()),
            StructField("ib_upper_bound", LongType()),
            StructField("ignore", StringType(), True),
        ]
    ),
    "inventory": StructType(
        [
            StructField("inv_date_sk", IDENTIFIER_INT, nullable=False),
            StructField("inv_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("inv_warehouse_sk", IDENTIFIER_INT, nullable=False),
            StructField("inv_quantity_on_hand", LongType()),
            StructField("ignore", StringType(), True),
        ]
    ),
    "item": StructType(
        [
            StructField("i_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("i_item_id", CharType(16), nullable=False),
            StructField("i_rec_start_date", DateType()),
            StructField("i_rec_end_date", DateType()),
            StructField("i_item_desc", VarcharType(200)),
            StructField("i_current_price", DecimalType(7, 2)),
            StructField("i_wholesale_cost", DecimalType(7, 2)),
            StructField("i_brand_id", LongType()),
            StructField("i_brand", CharType(50)),
            StructField("i_class_id", LongType()),
            StructField("i_class", CharType(50)),
            StructField("i_category_id", LongType()),
            StructField("i_category", CharType(50)),
            StructField("i_manufact_id", LongType()),
            StructField("i_manufact", CharType(50)),
            StructField("i_size", CharType(20)),
            StructField("i_formulation", CharType(20)),
            StructField("i_color", CharType(20)),
            StructField("i_units", CharType(10)),
            StructField("i_container", CharType(10)),
            StructField("i_manager_id", LongType()),
            StructField("i_product_name", CharType(50)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "promotion": StructType(
        [
            StructField("p_promo_sk", IDENTIFIER_INT, nullable=False),
            StructField("p_promo_id", CharType(16), nullable=False),
            StructField("p_start_date_sk", IDENTIFIER_INT),
            StructField("p_end_date_sk", IDENTIFIER_INT),
            StructField("p_item_sk", IDENTIFIER_INT),
            StructField("p_cost", DecimalType(15, 2)),
            StructField("p_response_target", LongType()),
            StructField("p_promo_name", CharType(50)),
            StructField("p_channel_dmail", CharType(1)),
            StructField("p_channel_email", CharType(1)),
            StructField("p_channel_catalog", CharType(1)),
            StructField("p_channel_tv", CharType(1)),
            StructField("p_channel_radio", CharType(1)),
            StructField("p_channel_press", CharType(1)),
            StructField("p_channel_event", CharType(1)),
            StructField("p_channel_demo", CharType(1)),
            StructField("p_channel_details", VarcharType(100)),
            StructField("p_purpose", CharType(15)),
            StructField("p_discount_active", CharType(1)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "reason": StructType(
        [
            StructField("r_reason_sk", IDENTIFIER_INT, nullable=False),
            StructField("r_reason_id", CharType(16), nullable=False),
            StructField("r_reason_desc", CharType(100)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "ship_mode": StructType(
        [
            StructField("sm_ship_mode_sk", IDENTIFIER_INT, nullable=False),
            StructField("sm_ship_mode_id", CharType(16), nullable=False),
            StructField("sm_type", CharType(30)),
            StructField("sm_code", CharType(10)),
            StructField("sm_carrier", CharType(20)),
            StructField("sm_contract", CharType(20)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "store": StructType(
        [
            StructField("s_store_sk", IDENTIFIER_INT, nullable=False),
            StructField("s_store_id", CharType(16), nullable=False),
            StructField("s_rec_start_date", DateType()),
            StructField("s_rec_end_date", DateType()),
            StructField("s_closed_date_sk", IDENTIFIER_INT),
            StructField("s_store_name", VarcharType(50)),
            StructField("s_number_employees", LongType()),
            StructField("s_floor_space", LongType()),
            StructField("s_hours", CharType(20)),
            StructField("s_manager", VarcharType(40)),
            StructField("s_market_id", LongType()),
            StructField("s_geography_class", VarcharType(100)),
            StructField("s_market_desc", VarcharType(100)),
            StructField("s_market_manager", VarcharType(40)),
            StructField("s_division_id", LongType()),
            StructField("s_division_name", VarcharType(50)),
            StructField("s_company_id", LongType()),
            StructField("s_company_name", VarcharType(50)),
            StructField("s_street_number", VarcharType(10)),
            StructField("s_street_name", VarcharType(60)),
            StructField("s_street_type", CharType(15)),
            StructField("s_suite_number", CharType(10)),
            StructField("s_city", VarcharType(60)),
            StructField("s_county", VarcharType(30)),
            StructField("s_state", CharType(2)),
            StructField("s_zip", CharType(10)),
            StructField("s_country", VarcharType(20)),
            StructField("s_gmt_offset", DecimalType(5, 2)),
            StructField("s_tax_precentage", DecimalType(5, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "store_returns": StructType(
        [
            StructField("sr_returned_date_sk", IDENTIFIER_INT),
            StructField("sr_return_time_sk", IDENTIFIER_INT),
            StructField("sr_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("sr_customer_sk", IDENTIFIER_INT),
            StructField("sr_cdemo_sk", IDENTIFIER_INT),
            StructField("sr_hdemo_sk", IDENTIFIER_INT),
            StructField("sr_addr_sk", IDENTIFIER_INT),
            StructField("sr_store_sk", IDENTIFIER_INT),
            StructField("sr_reason_sk", IDENTIFIER_INT),
            # Use LongType due to https://github.com/NVIDIA/spark-rapids-benchmarks/pull/9#issuecomment-1138379596
            # Databricks is using LongType as well in their accepted benchmark reports.
            # See https://www.tpc.org/results/supporting_files/tpcds/databricks~tpcds~100000~databricks_SQL_8.3~sup-1~2021-11-02~v01.zip
            StructField("sr_ticket_number", IDENTIFIER_LONG, nullable=False),
            StructField("sr_return_quantity", LongType()),
            StructField("sr_return_amt", DecimalType(7, 2)),
            StructField("sr_return_tax", DecimalType(7, 2)),
            StructField("sr_return_amt_inc_tax", DecimalType(7, 2)),
            StructField("sr_fee", DecimalType(7, 2)),
            StructField("sr_return_ship_cost", DecimalType(7, 2)),
            StructField("sr_refunded_cash", DecimalType(7, 2)),
            StructField("sr_reversed_charge", DecimalType(7, 2)),
            StructField("sr_store_credit", DecimalType(7, 2)),
            StructField("sr_net_loss", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "store_sales": StructType(
        [
            StructField("ss_sold_date_sk", IDENTIFIER_INT),
            StructField("ss_sold_time_sk", IDENTIFIER_INT),
            StructField("ss_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("ss_customer_sk", IDENTIFIER_INT),
            StructField("ss_cdemo_sk", IDENTIFIER_INT),
            StructField("ss_hdemo_sk", IDENTIFIER_INT),
            StructField("ss_addr_sk", IDENTIFIER_INT),
            StructField("ss_store_sk", IDENTIFIER_INT),
            StructField("ss_promo_sk", IDENTIFIER_INT),
            StructField("ss_ticket_number", IDENTIFIER_LONG, nullable=False),
            StructField("ss_quantity", LongType()),
            StructField("ss_wholesale_cost", DecimalType(7, 2)),
            StructField("ss_list_price", DecimalType(7, 2)),
            StructField("ss_sales_price", DecimalType(7, 2)),
            StructField("ss_ext_discount_amt", DecimalType(7, 2)),
            StructField("ss_ext_sales_price", DecimalType(7, 2)),
            StructField("ss_ext_wholesale_cost", DecimalType(7, 2)),
            StructField("ss_ext_list_price", DecimalType(7, 2)),
            StructField("ss_ext_tax", DecimalType(7, 2)),
            StructField("ss_coupon_amt", DecimalType(7, 2)),
            StructField("ss_net_paid", DecimalType(7, 2)),
            StructField("ss_net_paid_inc_tax", DecimalType(7, 2)),
            StructField("ss_net_profit", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "time_dim": StructType(
        [
            StructField("t_time_sk", IDENTIFIER_INT, nullable=False),
            StructField("t_time_id", CharType(16), nullable=False),
            StructField("t_time", LongType(), nullable=False),
            StructField("t_hour", LongType()),
            StructField("t_minute", LongType()),
            StructField("t_second", LongType()),
            StructField("t_am_pm", CharType(2)),
            StructField("t_shift", CharType(20)),
            StructField("t_sub_shift", CharType(20)),
            StructField("t_meal_time", CharType(20)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "warehouse": StructType(
        [
            StructField("w_warehouse_sk", IDENTIFIER_INT, nullable=False),
            StructField("w_warehouse_id", CharType(16), nullable=False),
            StructField("w_warehouse_name", VarcharType(20)),
            StructField("w_warehouse_sq_ft", LongType()),
            StructField("w_street_number", CharType(10)),
            StructField("w_street_name", VarcharType(60)),
            StructField("w_street_type", CharType(15)),
            StructField("w_suite_number", CharType(10)),
            StructField("w_city", VarcharType(60)),
            StructField("w_county", VarcharType(30)),
            StructField("w_state", CharType(2)),
            StructField("w_zip", CharType(10)),
            StructField("w_country", VarcharType(20)),
            StructField("w_gmt_offset", DecimalType(5, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "web_page": StructType(
        [
            StructField("wp_web_page_sk", IDENTIFIER_INT, nullable=False),
            StructField("wp_web_page_id", CharType(16), nullable=False),
            StructField("wp_rec_start_date", DateType()),
            StructField("wp_rec_end_date", DateType()),
            StructField("wp_creation_date_sk", IDENTIFIER_INT),
            StructField("wp_access_date_sk", IDENTIFIER_INT),
            StructField("wp_autogen_flag", CharType(1)),
            StructField("wp_customer_sk", IDENTIFIER_INT),
            StructField("wp_url", VarcharType(100)),
            StructField("wp_type", CharType(50)),
            StructField("wp_char_count", LongType()),
            StructField("wp_link_count", LongType()),
            StructField("wp_image_count", LongType()),
            StructField("wp_max_ad_count", LongType()),
            StructField("ignore", StringType(), True),
        ]
    ),
    "web_returns": StructType(
        [
            StructField("wr_returned_date_sk", IDENTIFIER_INT),
            StructField("wr_returned_time_sk", IDENTIFIER_INT),
            StructField("wr_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("wr_refunded_customer_sk", IDENTIFIER_INT),
            StructField("wr_refunded_cdemo_sk", IDENTIFIER_INT),
            StructField("wr_refunded_hdemo_sk", IDENTIFIER_INT),
            StructField("wr_refunded_addr_sk", IDENTIFIER_INT),
            StructField("wr_returning_customer_sk", IDENTIFIER_INT),
            StructField("wr_returning_cdemo_sk", IDENTIFIER_INT),
            StructField("wr_returning_hdemo_sk", IDENTIFIER_INT),
            StructField("wr_returning_addr_sk", IDENTIFIER_INT),
            StructField("wr_web_page_sk", IDENTIFIER_INT),
            StructField("wr_reason_sk", IDENTIFIER_INT),
            StructField("wr_order_number", IDENTIFIER_INT, nullable=False),
            StructField("wr_return_quantity", LongType()),
            StructField("wr_return_amt", DecimalType(7, 2)),
            StructField("wr_return_tax", DecimalType(7, 2)),
            StructField("wr_return_amt_inc_tax", DecimalType(7, 2)),
            StructField("wr_fee", DecimalType(7, 2)),
            StructField("wr_return_ship_cost", DecimalType(7, 2)),
            StructField("wr_refunded_cash", DecimalType(7, 2)),
            StructField("wr_reversed_charge", DecimalType(7, 2)),
            StructField("wr_account_credit", DecimalType(7, 2)),
            StructField("wr_net_loss", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "web_sales": StructType(
        [
            StructField("ws_sold_date_sk", IDENTIFIER_INT),
            StructField("ws_sold_time_sk", IDENTIFIER_INT),
            StructField("ws_ship_date_sk", IDENTIFIER_INT),
            StructField("ws_item_sk", IDENTIFIER_INT, nullable=False),
            StructField("ws_bill_customer_sk", IDENTIFIER_INT),
            StructField("ws_bill_cdemo_sk", IDENTIFIER_INT),
            StructField("ws_bill_hdemo_sk", IDENTIFIER_INT),
            StructField("ws_bill_addr_sk", IDENTIFIER_INT),
            StructField("ws_ship_customer_sk", IDENTIFIER_INT),
            StructField("ws_ship_cdemo_sk", IDENTIFIER_INT),
            StructField("ws_ship_hdemo_sk", IDENTIFIER_INT),
            StructField("ws_ship_addr_sk", IDENTIFIER_INT),
            StructField("ws_web_page_sk", IDENTIFIER_INT),
            StructField("ws_web_site_sk", IDENTIFIER_INT),
            StructField("ws_ship_mode_sk", IDENTIFIER_INT),
            StructField("ws_warehouse_sk", IDENTIFIER_INT),
            StructField("ws_promo_sk", IDENTIFIER_INT),
            StructField("ws_order_number", IDENTIFIER_INT, nullable=False),
            StructField("ws_quantity", LongType()),
            StructField("ws_wholesale_cost", DecimalType(7, 2)),
            StructField("ws_list_price", DecimalType(7, 2)),
            StructField("ws_sales_price", DecimalType(7, 2)),
            StructField("ws_ext_discount_amt", DecimalType(7, 2)),
            StructField("ws_ext_sales_price", DecimalType(7, 2)),
            StructField("ws_ext_wholesale_cost", DecimalType(7, 2)),
            StructField("ws_ext_list_price", DecimalType(7, 2)),
            StructField("ws_ext_tax", DecimalType(7, 2)),
            StructField("ws_coupon_amt", DecimalType(7, 2)),
            StructField("ws_ext_ship_cost", DecimalType(7, 2)),
            StructField("ws_net_paid", DecimalType(7, 2)),
            StructField("ws_net_paid_inc_tax", DecimalType(7, 2)),
            StructField("ws_net_paid_inc_ship", DecimalType(7, 2)),
            StructField("ws_net_paid_inc_ship_tax", DecimalType(7, 2)),
            StructField("ws_net_profit", DecimalType(7, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
    "web_site": StructType(
        [
            StructField("web_site_sk", IDENTIFIER_INT, nullable=False),
            StructField("web_site_id", CharType(16), nullable=False),
            StructField("web_rec_start_date", DateType()),
            StructField("web_rec_end_date", DateType()),
            StructField("web_name", VarcharType(50)),
            StructField("web_open_date_sk", IDENTIFIER_INT),
            StructField("web_close_date_sk", IDENTIFIER_INT),
            StructField("web_class", VarcharType(50)),
            StructField("web_manager", VarcharType(40)),
            StructField("web_mkt_id", LongType()),
            StructField("web_mkt_class", VarcharType(50)),
            StructField("web_mkt_desc", VarcharType(100)),
            StructField("web_market_manager", VarcharType(40)),
            StructField("web_company_id", LongType()),
            StructField("web_company_name", CharType(50)),
            StructField("web_street_number", CharType(10)),
            StructField("web_street_name", VarcharType(60)),
            StructField("web_street_type", CharType(15)),
            StructField("web_suite_number", CharType(10)),
            StructField("web_city", VarcharType(60)),
            StructField("web_county", VarcharType(30)),
            StructField("web_state", CharType(2)),
            StructField("web_zip", CharType(10)),
            StructField("web_country", VarcharType(20)),
            StructField("web_gmt_offset", DecimalType(5, 2)),
            StructField("web_tax_percentage", DecimalType(5, 2)),
            StructField("ignore", StringType(), True),
        ]
    ),
}


def get_tables_and_ext(benchmark: BenchmarkT) -> tuple[list[str], str]:
    if benchmark == "tpc-h":
        return TPC_H_TABLES, TPC_H_EXT
    elif benchmark == "tpc-ds":
        return TPC_DS_TABLES, TPC_DS_EXT
    else:
        raise ValueError(f"unknown benchmark '{benchmark}'")


def get_schema(table: str, benchmark: BenchmarkT) -> StructType:
    if benchmark == "tpc-h":
        return TPC_H_SCHEMAS[table]
    elif benchmark == "tpc-ds":
        return TPC_DS_SCHEMAS[table]
    else:
        raise ValueError(f"unknown benchmark '{benchmark}'")


def to_parquet(spark: SparkSession, src: str, dst: str, benchmark: BenchmarkT) -> None:
    tables, ext = get_tables_and_ext(benchmark)
    for i, table in enumerate(tables):
        df = spark.read.csv(
            f"{src}/{table}.{ext}",
            sep="|",
            header=False,
            schema=get_schema(table, benchmark),
            enforceSchema=True,
        )
        df = df.drop(df.columns[-1])
        df.write.mode("overwrite").parquet(f"{dst}/{table}")
        print(f"[to_parquet][{i+1:02}/{len(tables):02}] {table}")


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
