# Databricks notebook source
# MAGIC %md
# MAGIC # 🎉 Capstone Project - Final Working Version
# MAGIC 
# MAGIC This version has proper data type handling!
# MAGIC 
# MAGIC **Just Run All cells!**

# COMMAND ----------

# Configuration
CATALOG = "omar"
SCHEMA = "sbit_db"
VOLUME = "capstone_data"

volume_base = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

print(f"📊 Configuration:")
print(f"   Catalog: {CATALOG}")
print(f"   Schema: {SCHEMA}")
print(f"   Volume: {volume_base}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Generate Sample Data

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random

print("Creating directories...")
dirs = [
    f"{volume_base}/raw/registered_users_bz",
    f"{volume_base}/raw/gym_logins_bz",
    f"{volume_base}/test_data"
]

for d in dirs:
    dbutils.fs.mkdirs(d)

print("✅ Directories created")

# COMMAND ----------

# Generate users with proper schema
print("Generating users...")

user_schema = StructType([
    StructField("user_id", LongType(), False),
    StructField("device_id", LongType(), False),
    StructField("mac_address", StringType(), False),
    StructField("registration_timestamp", DoubleType(), False)
])

user_data = []
for i in range(1, 11):
    user_data.append((
        i,  # user_id as long
        1000 + i,  # device_id as long
        f"AA:BB:CC:DD:EE:{i:02d}",
        float(1609459200 + (i * 86400))  # timestamp as double
    ))

df_users = spark.createDataFrame(user_data, schema=user_schema)

# Write to volume
df_users.write.mode("overwrite").option("header", "true").csv(f"{volume_base}/raw/registered_users_bz/")

print("✅ Users generated")
display(df_users.limit(3))

# COMMAND ----------

# Generate gym logins with proper schema
print("Generating gym logins...")

gym_schema = StructType([
    StructField("mac_address", StringType(), False),
    StructField("gym", LongType(), False),
    StructField("login", DoubleType(), False),
    StructField("logout", DoubleType(), False)
])

gym_data = []
base_time = 1609459200.0

for i in range(1, 17):
    user_idx = (i % 10) + 1
    gym_data.append((
        f"AA:BB:CC:DD:EE:{user_idx:02d}",
        random.choice([1, 2, 3, 4, 5]),
        base_time + (i * 3600),
        base_time + (i * 3600) + 7200
    ))

df_gym = spark.createDataFrame(gym_data, schema=gym_schema)
df_gym.write.mode("overwrite").option("header", "true").csv(f"{volume_base}/raw/gym_logins_bz/")

print("✅ Gym logins generated")
display(df_gym.limit(3))

# COMMAND ----------

# Generate date lookup
print("Generating date lookup...")

from datetime import date

date_data = []
start_date = date(2021, 1, 1)

for day_num in range(365):
    current_date = start_date + timedelta(days=day_num)
    week_of_year = current_date.isocalendar()[1]
    
    date_data.append({
        "date": current_date.isoformat(),
        "week": week_of_year,
        "year": current_date.year,
        "month": current_date.month,
        "dayofweek": current_date.weekday() + 1,
        "dayofmonth": current_date.day,
        "dayofyear": day_num + 1,
        "week_part": f"{current_date.year}-W{week_of_year:02d}"
    })

df_date = spark.createDataFrame(date_data)
df_date.write.mode("overwrite").json(f"{volume_base}/test_data/")

print("✅ Date lookup generated (365 days)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Database & Tables

# COMMAND ----------

print("Creating database...")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print("✅ Database ready")

# COMMAND ----------

# Create Bronze tables
print("Creating Bronze tables...")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.registered_users_bz(
    user_id long,
    device_id long,
    mac_address string,
    registration_timestamp double,
    load_time timestamp,
    source_file string
) USING DELTA
""")
print("✅ registered_users_bz")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.gym_logins_bz(
    mac_address string,
    gym bigint,
    login double,
    logout double,
    load_time timestamp,
    source_file string
) USING DELTA
""")
print("✅ gym_logins_bz")

# COMMAND ----------

# Create Silver tables
print("Creating Silver tables...")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.users(
    user_id bigint,
    device_id bigint,
    mac_address string,
    registration_timestamp timestamp
) USING DELTA
""")
print("✅ users")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.gym_logs(
    mac_address string,
    gym bigint,
    login timestamp,
    logout timestamp
) USING DELTA
""")
print("✅ gym_logs")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.date_lookup(
    date date,
    week int,
    year int,
    month int,
    dayofweek int,
    dayofmonth int,
    dayofyear int,
    week_part string
) USING DELTA
""")
print("✅ date_lookup")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Load Data with Proper Types

# COMMAND ----------

print("Loading date lookup...")

spark.sql(f"""
INSERT OVERWRITE TABLE {CATALOG}.{SCHEMA}.date_lookup
SELECT 
    cast(date as date),
    cast(week as int),
    cast(year as int),
    cast(month as int),
    cast(dayofweek as int),
    cast(dayofmonth as int),
    cast(dayofyear as int),
    week_part
FROM json.`{volume_base}/test_data/`
""")

date_count = spark.table(f"{CATALOG}.{SCHEMA}.date_lookup").count()
print(f"✅ date_lookup loaded: {date_count} records")

# COMMAND ----------

print("Loading registered_users_bz...")

# Read CSV with proper types
df_users_bronze = spark.read.option("header", "true").csv(f"{volume_base}/raw/registered_users_bz/") \
    .select(
        F.col("user_id").cast("long"),
        F.col("device_id").cast("long"),
        F.col("mac_address"),
        F.col("registration_timestamp").cast("double"),
        F.current_timestamp().alias("load_time"),
        F.lit("generated").alias("source_file")
    )

# Write to Delta table
df_users_bronze.write.mode("overwrite").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.registered_users_bz")

users_bz_count = spark.table(f"{CATALOG}.{SCHEMA}.registered_users_bz").count()
print(f"✅ registered_users_bz loaded: {users_bz_count} records")

# COMMAND ----------

print("Transforming to Silver users...")

df_users_silver = spark.table(f"{CATALOG}.{SCHEMA}.registered_users_bz") \
    .select(
        F.col("user_id").cast("bigint"),
        F.col("device_id").cast("bigint"),
        F.col("mac_address"),
        F.from_unixtime(F.col("registration_timestamp")).cast("timestamp").alias("registration_timestamp")
    ).dropDuplicates(["user_id"])

df_users_silver.write.mode("overwrite").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.users")

users_count = spark.table(f"{CATALOG}.{SCHEMA}.users").count()
print(f"✅ users loaded: {users_count} records")

# COMMAND ----------

print("Loading gym_logins_bz...")

df_gym_bronze = spark.read.option("header", "true").csv(f"{volume_base}/raw/gym_logins_bz/") \
    .select(
        F.col("mac_address"),
        F.col("gym").cast("bigint"),
        F.col("login").cast("double"),
        F.col("logout").cast("double"),
        F.current_timestamp().alias("load_time"),
        F.lit("generated").alias("source_file")
    )

df_gym_bronze.write.mode("overwrite").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.gym_logins_bz")

gym_bz_count = spark.table(f"{CATALOG}.{SCHEMA}.gym_logins_bz").count()
print(f"✅ gym_logins_bz loaded: {gym_bz_count} records")

# COMMAND ----------

print("Transforming to Silver gym_logs...")

df_gym_silver = spark.table(f"{CATALOG}.{SCHEMA}.gym_logins_bz") \
    .select(
        F.col("mac_address"),
        F.col("gym").cast("bigint"),
        F.from_unixtime(F.col("login")).cast("timestamp").alias("login"),
        F.from_unixtime(F.col("logout")).cast("timestamp").alias("logout")
    ).dropDuplicates(["mac_address", "gym", "login"])

df_gym_silver.write.mode("overwrite").format("delta").saveAsTable(f"{CATALOG}.{SCHEMA}.gym_logs")

gym_count = spark.table(f"{CATALOG}.{SCHEMA}.gym_logs").count()
print(f"✅ gym_logs loaded: {gym_count} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Gold Layer

# COMMAND ----------

print("Creating Gold layer view...")

spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.gym_summary AS
SELECT 
    to_date(login) as date,
    gym,
    l.mac_address,
    round((unix_timestamp(logout) - unix_timestamp(login))/60, 2) as minutes_in_gym
FROM {CATALOG}.{SCHEMA}.gym_logs l
ORDER BY date, gym, l.mac_address
""")

summary_count = spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.gym_summary").count()
print(f"✅ gym_summary created: {summary_count} records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Verify Results

# COMMAND ----------

tables = spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").collect()

print("=" * 70)
print(f"📊 CAPSTONE PROJECT RESULTS")
print("=" * 70)
print()

bronze = [t.tableName for t in tables if "_bz" in t.tableName]
gold = [t.tableName for t in tables if t.tableName == "gym_summary"]
silver = [t.tableName for t in tables if t.tableName not in bronze and t.tableName not in gold]

print(f"🥉 Bronze Layer ({len(bronze)} tables):")
for t in bronze:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
    print(f"   ✅ {t}: {count:,} records")

print(f"\n🥈 Silver Layer ({len(silver)} tables):")
for t in silver:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
    print(f"   ✅ {t}: {count:,} records")

print(f"\n🥇 Gold Layer ({len(gold)} views):")
for t in gold:
    count = spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.{t}").count()
    print(f"   ✅ {t}: {count:,} records")

print(f"\n📊 Total: {len(tables)} tables/views created!")
print()
print("=" * 70)
print("🎉 CAPSTONE PROJECT COMPLETE!")
print("=" * 70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC -- View users
# MAGIC SELECT * FROM omar.sbit_db.users LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- View gym summary
# MAGIC SELECT * FROM omar.sbit_db.gym_summary LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Record counts
# MAGIC SELECT 'users' as table_name, COUNT(*) as records FROM omar.sbit_db.users
# MAGIC UNION ALL
# MAGIC SELECT 'gym_logs', COUNT(*) FROM omar.sbit_db.gym_logs
# MAGIC UNION ALL
# MAGIC SELECT 'date_lookup', COUNT(*) FROM omar.sbit_db.date_lookup
# MAGIC UNION ALL
# MAGIC SELECT 'gym_summary', COUNT(*) FROM omar.sbit_db.gym_summary
# MAGIC ORDER BY table_name

# COMMAND ----------

# MAGIC %md
# MAGIC # 🎊 Congratulations!
# MAGIC 
# MAGIC You've successfully completed the Databricks Capstone Project!
# MAGIC 
# MAGIC ## What You Built:
# MAGIC 
# MAGIC ✅ **Medallion Architecture** - Bronze, Silver, Gold layers  
# MAGIC ✅ **Unity Catalog** - Data governance with catalog.schema.table  
# MAGIC ✅ **Delta Lake** - ACID transactions and versioning  
# MAGIC ✅ **Data Pipeline** - ETL with transformations  
# MAGIC ✅ **Analytics** - Business-ready views  
# MAGIC 
# MAGIC ## Skills Demonstrated:
# MAGIC 
# MAGIC - Data ingestion from CSV/JSON
# MAGIC - Schema management and type casting
# MAGIC - Data quality and deduplication
# MAGIC - Aggregations and transformations
# MAGIC - View creation for analytics
# MAGIC 
# MAGIC **Well done! 🚀**

# COMMAND ----------


