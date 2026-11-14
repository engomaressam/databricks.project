# Databricks notebook source
# MAGIC %md
# MAGIC # Complete Capstone Project - All-in-One
# MAGIC 
# MAGIC This notebook does EVERYTHING in one place:
# MAGIC - Generates sample data
# MAGIC - Creates all tables
# MAGIC - Runs the entire pipeline
# MAGIC - Shows results
# MAGIC 
# MAGIC **Just attach a cluster and Run All!**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Configuration
CATALOG = "omar"
SCHEMA = "sbit_db"
VOLUME = "capstone_data"

volume_base = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"
checkpoint_base = f"/Volumes/{CATALOG}/{SCHEMA}/capstone_checkpoints"

print(f"Catalog: {CATALOG}")
print(f"Schema: {SCHEMA}")
print(f"Volume: {volume_base}")
print(f"Checkpoints: {checkpoint_base}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Generate Sample Data

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random

print("Creating volume directories...")

# Create directories
dirs = [
    f"{volume_base}/raw/registered_users_bz",
    f"{volume_base}/raw/gym_logins_bz",
    f"{volume_base}/raw/kafka_multiplex_bz",
    f"{volume_base}/test_data"
]

for d in dirs:
    dbutils.fs.mkdirs(d)
    print(f"{d}")

# COMMAND ----------

# Generate Registered Users
print("Generating registered users...")

user_data = []
for i in range(1, 11):
    user_data.append({
        "user_id": i,
        "device_id": 1000 + i,
        "mac_address": f"AA:BB:CC:DD:EE:{i:02d}",
        "registration_timestamp": 1609459200 + (i * 86400)
    })

df_users = spark.createDataFrame(user_data)
df_users.limit(5).write.mode("overwrite").option("header", "true").csv(f"{volume_base}/raw/registered_users_bz/")
df_users.filter(F.col("user_id") > 5).write.mode("append").option("header", "true").csv(f"{volume_base}/raw/registered_users_bz/")

print("Registered users created")

# COMMAND ----------

# Generate Gym Logins
print("Generating gym logins...")

gym_data = []
base_time = 1609459200

for i in range(1, 17):
    user_idx = (i % 10) + 1
    gym_data.append({
        "mac_address": f"AA:BB:CC:DD:EE:{user_idx:02d}",
        "gym": random.choice([1, 2, 3, 4, 5]),
        "login": base_time + (i * 3600),
        "logout": base_time + (i * 3600) + 7200
    })

df_gym = spark.createDataFrame(gym_data)
df_gym.write.mode("overwrite").option("header", "true").csv(f"{volume_base}/raw/gym_logins_bz/")

print("Gym logins created")

# COMMAND ----------

# Generate User Info (JSON)
print("Generating user info...")

user_info_data = []
for i in range(1, 11):
    user_info_data.append({
        "user_id": i,
        "update_type": "new",
        "timestamp": 1609459200.0 + (i * 86400),
        "dob": f"01/{i:02d}/1990",
        "sex": random.choice(["M", "F"]),
        "gender": random.choice(["Male", "Female"]),
        "first_name": f"User{i}",
        "last_name": f"Test{i}",
        "address": {
            "street_address": f"{i}00 Main St",
            "city": random.choice(["New York", "Los Angeles", "Chicago"]),
            "state": random.choice(["NY", "CA", "IL"]),
            "zip": 10000 + i
        }
    })

df_user_info = spark.createDataFrame(user_info_data)
df_user_info.write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/user_info/")

print("User info created")

# COMMAND ----------

# Generate BPM Data
print("Generating BPM data (simplified)...")

bpm_data = []
base_ts = datetime(2021, 1, 1, 10, 0, 0)

for user_id in range(1, 6):
    device_id = 1000 + user_id
    for minute in range(0, 60, 10):  # Reduced data
        timestamp = base_ts + timedelta(minutes=minute)
        bpm_data.append({
            "device_id": device_id,
            "time": timestamp.isoformat(),
            "heartrate": random.randint(60, 180)
        })

df_bpm = spark.createDataFrame(bpm_data)
df_bpm.write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/bpm/")

print(f"BPM data created ({len(bpm_data)} records)")

# COMMAND ----------

# Generate Workout Data
print("Generating workout data...")

workout_data = []
base_ts = datetime(2021, 1, 1, 10, 0, 0)

session_id = 1
for user_id in range(1, 9):
    workout_id = random.choice([1, 2, 3])
    start_time = base_ts + timedelta(hours=user_id)
    end_time = start_time + timedelta(hours=1)
    
    workout_data.append({
        "user_id": (user_id % 5) + 1,
        "workout_id": workout_id,
        "time": start_time.timestamp(),
        "action": "start",
        "session_id": session_id
    })
    
    workout_data.append({
        "user_id": (user_id % 5) + 1,
        "workout_id": workout_id,
        "time": end_time.timestamp(),
        "action": "stop",
        "session_id": session_id
    })
    
    session_id += 1

df_workout = spark.createDataFrame(workout_data)
df_workout.write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/workout/")

print("Workout data created")

# COMMAND ----------

# Generate Date Lookup
print("Generating date lookup...")

from datetime import date

date_lookup = []
start_date = date(2021, 1, 1)

for day_num in range(365):
    current_date = start_date + timedelta(days=day_num)
    week_of_year = current_date.isocalendar()[1]
    
    date_lookup.append({
        "date": current_date.isoformat(),
        "week": week_of_year,
        "year": current_date.year,
        "month": current_date.month,
        "dayofweek": current_date.weekday() + 1,
        "dayofmonth": current_date.day,
        "dayofyear": day_num + 1,
        "week_part": f"{current_date.year}-W{week_of_year:02d}"
    })

df_date = spark.createDataFrame(date_lookup)
df_date.write.mode("overwrite").json(f"{volume_base}/test_data/")

print("Date lookup created (365 days)")
print("\nAll sample data generated!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Database Schema

# COMMAND ----------

print(f"Creating database {CATALOG}.{SCHEMA}...")

spark.sql(f"CREATE DATABASE IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE {CATALOG}.{SCHEMA}")

print("Database ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create All Tables

# COMMAND ----------

print("Creating tables...")

# Bronze tables
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.registered_users_bz(
    user_id long,
    device_id long,
    mac_address string,
    registration_timestamp double,
    load_time timestamp,
    source_file string
)
""")
print("registered_users_bz")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.gym_logins_bz(
    mac_address string,
    gym bigint,
    login double,
    logout double,
    load_time timestamp,
    source_file string
)
""")
print("gym_logins_bz")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.kafka_multiplex_bz(
    key string,
    value string,
    topic string,
    partition bigint,
    offset bigint,
    timestamp bigint,
    date date,
    week_part string,
    load_time timestamp,
    source_file string
) PARTITIONED BY (topic, week_part)
""")
print("kafka_multiplex_bz")

# Silver tables
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.users(
    user_id bigint,
    device_id bigint,
    mac_address string,
    registration_timestamp timestamp
)
""")
print("users")

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.gym_logs(
    mac_address string,
    gym bigint,
    login timestamp,
    logout timestamp
)
""")
print("gym_logs")

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
)
""")
print("date_lookup")

print("\nAll tables created!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Load Data into Tables

# COMMAND ----------

print("Loading data into tables...")

# Load date lookup
spark.sql(f"""
INSERT OVERWRITE TABLE {CATALOG}.{SCHEMA}.date_lookup
SELECT date, week, year, month, dayofweek, dayofmonth, dayofyear, week_part
FROM json.`{volume_base}/test_data/`
""")
print("date_lookup loaded")

# Load users from bronze
df_users_bronze = spark.read.option("header", "true").csv(f"{volume_base}/raw/registered_users_bz/") \
    .withColumn("load_time", F.current_timestamp()) \
    .withColumn("source_file", F.lit("generated"))

df_users_bronze.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.registered_users_bz")
print("registered_users_bz loaded")

# Transform to silver users
df_users_silver = df_users_bronze.select(
    F.col("user_id").cast("bigint"),
    F.col("device_id").cast("bigint"),
    "mac_address",
    F.from_unixtime(F.col("registration_timestamp")).cast("timestamp").alias("registration_timestamp")
).dropDuplicates(["user_id"])

df_users_silver.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.users")
print("users loaded")

# Load gym logins
df_gym_bronze = spark.read.option("header", "true").csv(f"{volume_base}/raw/gym_logins_bz/") \
    .withColumn("load_time", F.current_timestamp()) \
    .withColumn("source_file", F.lit("generated"))

df_gym_bronze.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.gym_logins_bz")
print("gym_logins_bz loaded")

# Transform to silver gym_logs
df_gym_silver = df_gym_bronze.select(
    "mac_address",
    F.col("gym").cast("bigint"),
    F.from_unixtime(F.col("login")).cast("timestamp").alias("login"),
    F.from_unixtime(F.col("logout")).cast("timestamp").alias("logout")
).dropDuplicates(["mac_address", "gym", "login"])

df_gym_silver.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.gym_logs")
print("gym_logs loaded")

print("\nAll data loaded!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Gold Layer View

# COMMAND ----------

print("Creating gold layer...")

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
print("gym_summary view created")

print("\nGold layer complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Verify Results

# COMMAND ----------

tables = spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").collect()

print(f"Tables in {CATALOG}.{SCHEMA}:\n")

bronze = [t.tableName for t in tables if "_bz" in t.tableName]
gold = [t.tableName for t in tables if t.tableName in ["gym_summary"]]
silver = [t.tableName for t in tables if t.tableName not in bronze and t.tableName not in gold]

print(f"Bronze Layer ({len(bronze)} tables):")
for t in bronze:
    try:
        count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
        print(f"   {t}: {count:,} records")
    except:
        print(f"    {t}: Unable to count")

print(f"\nSilver Layer ({len(silver)} tables):")
for t in silver:
    try:
        count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
        print(f"   {t}: {count:,} records")
    except:
        print(f"    {t}: Unable to count")

print(f"\nGold Layer ({len(gold)} views):")
for t in gold:
    try:
        count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
        print(f"   {t}: {count:,} records")
    except:
        print(f"    {t}: Unable to count")

print(f"\nTotal: {len(tables)} tables/views created!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM omar.sbit_db.users LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM omar.sbit_db.gym_summary LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC # CAPSTONE PROJECT COMPLETE!
# MAGIC 
# MAGIC ## Summary
# MAGIC 
# MAGIC Sample data generated  
# MAGIC Database and tables created  
# MAGIC Bronze layer: Raw data  
# MAGIC Silver layer: Transformed data  
# MAGIC Gold layer: Analytics  
# MAGIC 
# MAGIC ## What You Built
# MAGIC 
# MAGIC - **Medallion Architecture** (Bronze/Silver/Gold)
# MAGIC - **Unity Catalog** integration
# MAGIC - **Delta Lake** tables
# MAGIC - **Data pipeline** with transformations
# MAGIC 
# MAGIC **Congratulations! **

# COMMAND ----------


