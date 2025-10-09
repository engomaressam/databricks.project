# Databricks notebook source
# MAGIC %md
# MAGIC # Data Upload Helper
# MAGIC This notebook helps upload the capstone dataset files to the Unity Catalog volume.
# MAGIC 
# MAGIC **Run this notebook from Databricks UI after uploading your dataset files to DBFS temp location**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 1: Upload via UI then copy to volume
# MAGIC 
# MAGIC 1. In Databricks UI, go to **Data** → **Upload Data**
# MAGIC 2. Upload all files from `CapstoneProject/Capstone Project/Data Set/`
# MAGIC 3. Note the uploaded path (usually `/FileStore/tables/...`)
# MAGIC 4. Run the cell below to copy to volume

# COMMAND ----------

# Update this path to where you uploaded the files
source_path = "/FileStore/tables/uploaded_data/"  # Change this!
dest_volume = "/Volumes/omar/sbit_db/capstone_data"

# Create directory structure in volume
dbutils.fs.mkdirs(f"{dest_volume}/raw/registered_users_bz")
dbutils.fs.mkdirs(f"{dest_volume}/raw/gym_logins_bz")
dbutils.fs.mkdirs(f"{dest_volume}/raw/kafka_multiplex_bz")
dbutils.fs.mkdirs(f"{dest_volume}/test_data")

# Copy files (update filenames as needed)
files_to_copy = {
    "1-registered_users_1.csv": f"{dest_volume}/raw/registered_users_bz/",
    "1-registered_users_2.csv": f"{dest_volume}/raw/registered_users_bz/",
    "5-gym_logins_1.csv": f"{dest_volume}/raw/gym_logins_bz/",
    "5-gym_logins_2.csv": f"{dest_volume}/raw/gym_logins_bz/",
    "2-user_info_1.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "2-user_info_2.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "3-bpm_1.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "3-bpm_2.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "4-workout_1.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "4-workout_2.json": f"{dest_volume}/raw/kafka_multiplex_bz/",
    "6-date-lookup.json": f"{dest_volume}/test_data/",
    "7-gym_summary_1.parquet": f"{dest_volume}/test_data/",
    "7-gym_summary_2.parquet": f"{dest_volume}/test_data/",
    "8-workout_bpm_summary_2.parquet": f"{dest_volume}/test_data/",
}

for filename, dest_dir in files_to_copy.items():
    try:
        dbutils.fs.cp(f"{source_path}/{filename}", f"{dest_dir}{filename}")
        print(f"✅ Copied: {filename}")
    except Exception as e:
        print(f"❌ Error copying {filename}: {e}")

print("\n✅ Data upload complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 2: Verify volume contents

# COMMAND ----------

display(dbutils.fs.ls("/Volumes/omar/sbit_db/capstone_data"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Method 3: Quick test - Generate sample data
# MAGIC For testing without all files, uncomment and run:

# COMMAND ----------

# from pyspark.sql.types import *
# from pyspark.sql import functions as F
#
# # Generate sample registered users
# df_users = spark.range(1, 6).select(
#     F.col("id").alias("user_id"),
#     (F.col("id") * 1000).alias("device_id"),
#     F.concat(F.lit("AA:BB:CC:DD:EE:"), F.col("id")).alias("mac_address"),
#     F.unix_timestamp(F.current_timestamp()).alias("registration_timestamp")
# )
#
# df_users.write.mode("overwrite").option("header", "true") \
#     .csv("/Volumes/omar/sbit_db/capstone_data/raw/registered_users_bz/")
#
# print("✅ Sample data generated")

# COMMAND ----------


