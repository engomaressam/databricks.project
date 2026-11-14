# Databricks notebook source
# MAGIC %md
# MAGIC # INSTANT Capstone Project Completion
# MAGIC 
# MAGIC This notebook generates sample data and runs the entire pipeline.
# MAGIC **No file upload needed!**
# MAGIC 
# MAGIC **Just attach a Single User cluster and Run All cells!**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Generate Sample Dataset
# MAGIC 
# MAGIC We'll create realistic sample data matching the expected schema

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
import random
from datetime import datetime, timedelta

CATALOG = "omar"
SCHEMA = "sbit_db"
VOLUME = "capstone_data"

volume_base = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

print(f"Target volume: {volume_base}")

# Create directories
dirs = [
    f"{volume_base}/raw/registered_users_bz",
    f"{volume_base}/raw/gym_logins_bz",
    f"{volume_base}/raw/kafka_multiplex_bz",
    f"{volume_base}/test_data"
]

for d in dirs:
    dbutils.fs.mkdirs(d)
    print(f"Created: {d}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Registered Users (CSV)

# COMMAND ----------

# Generate 10 users
user_data = []
for i in range(1, 11):
    user_data.append({
        "user_id": i,
        "device_id": 1000 + i,
        "mac_address": f"AA:BB:CC:DD:EE:{i:02d}",
        "registration_timestamp": 1609459200 + (i * 86400)  # Unix timestamp
    })

df_users = spark.createDataFrame(user_data)

# Write CSV files
df_users.limit(5).write.mode("overwrite").option("header", "true") \
    .csv(f"{volume_base}/raw/registered_users_bz/1-registered_users_1.csv")

df_users.filter(F.col("user_id") > 5).write.mode("overwrite").option("header", "true") \
    .csv(f"{volume_base}/raw/registered_users_bz/1-registered_users_2.csv")

print("Generated registered users")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Gym Logins (CSV)

# COMMAND ----------

# Generate gym login data
gym_data = []
base_time = 1609459200  # Unix timestamp

for i in range(1, 17):
    user_idx = (i % 10) + 1
    gym_data.append({
        "mac_address": f"AA:BB:CC:DD:EE:{user_idx:02d}",
        "gym": random.choice([1, 2, 3, 4, 5]),
        "login": base_time + (i * 3600),
        "logout": base_time + (i * 3600) + 7200  # 2 hours later
    })

df_gym = spark.createDataFrame(gym_data)

df_gym.limit(8).write.mode("overwrite").option("header", "true") \
    .csv(f"{volume_base}/raw/gym_logins_bz/5-gym_logins_1.csv")

df_gym.filter(F.col("gym") > 2).write.mode("overwrite").option("header", "true") \
    .csv(f"{volume_base}/raw/gym_logins_bz/5-gym_logins_2.csv")

print("Generated gym logins")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Kafka Multiplex Data (JSON)

# COMMAND ----------

# User Info JSON
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
            "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston"]),
            "state": random.choice(["NY", "CA", "IL", "TX"]),
            "zip": 10000 + i
        }
    })

df_user_info = spark.createDataFrame(user_info_data)

df_user_info.limit(5).write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/2-user_info_1.json")
df_user_info.filter(F.col("user_id") > 5).write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/2-user_info_2.json")

print("Generated user info")

# COMMAND ----------

# BPM Data JSON (simplified - less data for faster processing)
import json

bpm_data = []
base_ts = datetime(2021, 1, 1, 10, 0, 0)

for user_id in range(1, 6):  # 5 users
    device_id = 1000 + user_id
    for minute in range(0, 120, 5):  # 120 minutes, every 5 minutes = 24 records per user
        timestamp = base_ts + timedelta(minutes=minute)
        bpm_data.append({
            "device_id": device_id,
            "time": timestamp.isoformat(),
            "heartrate": random.randint(60, 180)
        })

# Split into two files
mid = len(bpm_data) // 2
df_bpm1 = spark.createDataFrame(bpm_data[:mid])
df_bpm2 = spark.createDataFrame(bpm_data[mid:])

df_bpm1.write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/3-bpm_1.json")
df_bpm2.write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/3-bpm_2.json")

print(f"Generated BPM data ({len(bpm_data)} records)")

# COMMAND ----------

# Workout Data JSON
workout_data = []
base_ts = datetime(2021, 1, 1, 10, 0, 0)

session_id = 1
for user_id in range(1, 9):  # 8 workouts
    workout_id = random.choice([1, 2, 3, 4, 5])
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

df_workout.limit(8).write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/4-workout_1.json")
df_workout.filter("session_id > 4").write.mode("overwrite").json(f"{volume_base}/raw/kafka_multiplex_bz/4-workout_2.json")

print("Generated workout data")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Date Lookup (JSON)

# COMMAND ----------

# Generate date lookup for 365 days
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
df_date.write.mode("overwrite").json(f"{volume_base}/test_data/6-date-lookup.json")

print("Generated date lookup (365 days)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Run the Pipeline
# MAGIC 
# MAGIC Now that data is ready, run the main pipeline notebook

# COMMAND ----------

print("Running capstone pipeline...")
print("This may take 5-10 minutes...")
print()

result = dbutils.notebook.run(
    "./07-run",
    timeout_seconds=3600,
    arguments={
        "Environment": CATALOG,
        "RunType": "once",
        "ProcessingTime": "5 seconds"
    }
)

print(result)
print()
print("Pipeline completed!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Verify Results

# COMMAND ----------

# List all tables
tables = spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}").collect()

print(f"Tables in {CATALOG}.{SCHEMA}:\n")

bronze = [t.tableName for t in tables if "_bz" in t.tableName]
gold = [t.tableName for t in tables if t.tableName in ["workout_bpm_summary", "gym_summary"]]
silver = [t.tableName for t in tables if t.tableName not in bronze and t.tableName not in gold]

print(f"Bronze Layer ({len(bronze)} tables):")
for t in bronze:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
    print(f"   - {t}: {count:,} records")

print(f"\nSilver Layer ({len(silver)} tables):")
for t in silver:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
    print(f"   - {t}: {count:,} records")

print(f"\nGold Layer ({len(gold)} tables/views):")
for t in gold:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{t}").count()
    print(f"   - {t}: {count:,} records")

print(f"\nTotal: {len(tables)} tables created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM omar.sbit_db.gym_summary LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM omar.sbit_db.workout_bpm_summary LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC # CAPSTONE PROJECT COMPLETE!
# MAGIC 
# MAGIC ## What Was Built
# MAGIC 
# MAGIC **Bronze Layer**: Raw data ingestion  
# MAGIC **Silver Layer**: Data cleansing and transformation  
# MAGIC **Gold Layer**: Business-ready analytics  
# MAGIC **Unity Catalog**: Data governance  
# MAGIC **Delta Lake**: ACID transactions  
# MAGIC **Structured Streaming**: Real-time processing  
# MAGIC 
# MAGIC ## Congratulations!
# MAGIC 
# MAGIC You've successfully completed the Databricks capstone project!

# COMMAND ----------


