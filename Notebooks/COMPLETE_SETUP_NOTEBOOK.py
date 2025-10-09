# Databricks notebook source
# MAGIC %md
# MAGIC # 🚀 Complete Capstone Project Setup & Execution
# MAGIC 
# MAGIC This notebook will:
# MAGIC 1. ✅ Upload dataset files to Unity Catalog volume
# MAGIC 2. ✅ Verify all data is in place
# MAGIC 3. ✅ Execute the complete pipeline (Bronze → Silver → Gold)
# MAGIC 4. ✅ Validate results
# MAGIC 
# MAGIC **Instructions:**
# MAGIC 1. Upload all files from `CapstoneProject/Capstone Project/Data Set/` to DBFS first
# MAGIC 2. Update the `source_path` variable below with your upload location
# MAGIC 3. Attach this notebook to a **Single User** cluster
# MAGIC 4. Run All cells
# MAGIC 
# MAGIC **OR** use the widget to upload files directly (if your cluster supports file upload)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Configuration
CATALOG_NAME = "omar"
SCHEMA_NAME = "sbit_db"
VOLUME_NAME = "capstone_data"

# Path where you uploaded the dataset files in DBFS
# Example: "/FileStore/tables/" or wherever you uploaded via UI
dbutils.widgets.text("source_path", "/FileStore/tables/", "Source Path (DBFS)")
source_path = dbutils.widgets.get("source_path")

volume_base = f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{VOLUME_NAME}"

print(f"Catalog: {CATALOG_NAME}")
print(f"Schema: {SCHEMA_NAME}")
print(f"Volume: {VOLUME_NAME}")
print(f"Source: {source_path}")
print(f"Destination: {volume_base}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Directory Structure in Volume

# COMMAND ----------

# Create directories
dirs_to_create = [
    f"{volume_base}/raw",
    f"{volume_base}/raw/registered_users_bz",
    f"{volume_base}/raw/gym_logins_bz",
    f"{volume_base}/raw/kafka_multiplex_bz",
    f"{volume_base}/test_data"
]

for dir_path in dirs_to_create:
    try:
        dbutils.fs.mkdirs(dir_path)
        print(f"✅ Created: {dir_path}")
    except Exception as e:
        print(f"ℹ️  {dir_path}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Upload Dataset Files to Volume
# MAGIC 
# MAGIC **If files are already in DBFS, this will copy them to the volume.**

# COMMAND ----------

# File mappings
file_mappings = {
    # Registered users
    "1-registered_users_1.csv": f"{volume_base}/raw/registered_users_bz/",
    "1-registered_users_2.csv": f"{volume_base}/raw/registered_users_bz/",
    
    # Gym logins
    "5-gym_logins_1.csv": f"{volume_base}/raw/gym_logins_bz/",
    "5-gym_logins_2.csv": f"{volume_base}/raw/gym_logins_bz/",
    
    # Kafka multiplex
    "2-user_info_1.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    "2-user_info_2.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    "3-bpm_1.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    "3-bpm_2.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    "4-workout_1.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    "4-workout_2.json": f"{volume_base}/raw/kafka_multiplex_bz/",
    
    # Test data
    "6-date-lookup.json": f"{volume_base}/test_data/",
    "7-gym_summary_1.parquet": f"{volume_base}/test_data/",
    "7-gym_summary_2.parquet": f"{volume_base}/test_data/",
    "8-workout_bpm_summary_2.parquet": f"{volume_base}/test_data/",
}

uploaded_count = 0
failed_count = 0

for filename, dest_dir in file_mappings.items():
    source_file = f"{source_path}{filename}"
    dest_file = f"{dest_dir}{filename}"
    
    try:
        # Check if source exists
        try:
            dbutils.fs.ls(source_file)
        except:
            print(f"⚠️  Source not found: {filename}")
            failed_count += 1
            continue
        
        # Copy file
        dbutils.fs.cp(source_file, dest_file, recurse=True)
        print(f"✅ Copied: {filename}")
        uploaded_count += 1
        
    except Exception as e:
        print(f"❌ Error copying {filename}: {e}")
        failed_count += 1

print(f"\n📊 Summary: {uploaded_count} uploaded, {failed_count} failed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Verify Files in Volume

# COMMAND ----------

print("📁 Volume contents:\n")

def list_recursively(path, indent=0):
    try:
        items = dbutils.fs.ls(path)
        for item in items:
            prefix = "  " * indent
            if item.isDir():
                print(f"{prefix}📁 {item.name}")
                list_recursively(item.path, indent + 1)
            else:
                size_mb = item.size / (1024*1024)
                print(f"{prefix}📄 {item.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"{prefix}❌ Error: {e}")

list_recursively(volume_base)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Run the Pipeline Notebook
# MAGIC 
# MAGIC This will execute the main pipeline (07-run) which creates all tables.

# COMMAND ----------

# Set parameters for the pipeline
dbutils.notebook.run(
    "./07-run",
    timeout_seconds=3600,  # 1 hour timeout
    arguments={
        "Environment": CATALOG_NAME,
        "RunType": "once",
        "ProcessingTime": "5 seconds"
    }
)

print("✅ Pipeline executed successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Verify Tables Created

# COMMAND ----------

# List all tables in the schema
tables = spark.sql(f"SHOW TABLES IN {CATALOG_NAME}.{SCHEMA_NAME}").collect()

print(f"📊 Tables in {CATALOG_NAME}.{SCHEMA_NAME}:\n")

bronze_tables = []
silver_tables = []
gold_tables = []

for table in tables:
    table_name = table.tableName
    table_type = "VIEW" if table.isTemporary else "TABLE"
    
    # Categorize
    if "_bz" in table_name:
        bronze_tables.append(table_name)
    elif table_name in ["workout_bpm_summary", "gym_summary"]:
        gold_tables.append(table_name)
    else:
        silver_tables.append(table_name)

print(f"🥉 Bronze Layer ({len(bronze_tables)} tables):")
for t in bronze_tables:
    print(f"   - {t}")

print(f"\n🥈 Silver Layer ({len(silver_tables)} tables):")
for t in silver_tables:
    print(f"   - {t}")

print(f"\n🥇 Gold Layer ({len(gold_tables)} tables):")
for t in gold_tables:
    print(f"   - {t}")

print(f"\n📊 Total: {len(tables)} tables/views created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Sample Data Validation

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check gym summary
# MAGIC SELECT * FROM omar.sbit_db.gym_summary LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check workout BPM summary  
# MAGIC SELECT * FROM omar.sbit_db.workout_bpm_summary LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Record counts by table
# MAGIC SELECT 'users' as table_name, COUNT(*) as record_count FROM omar.sbit_db.users
# MAGIC UNION ALL
# MAGIC SELECT 'gym_logs', COUNT(*) FROM omar.sbit_db.gym_logs
# MAGIC UNION ALL
# MAGIC SELECT 'completed_workouts', COUNT(*) FROM omar.sbit_db.completed_workouts
# MAGIC UNION ALL
# MAGIC SELECT 'workout_bpm_summary', COUNT(*) FROM omar.sbit_db.workout_bpm_summary
# MAGIC ORDER BY table_name

# COMMAND ----------

# MAGIC %md
# MAGIC # 🎉 Capstone Project Complete!
# MAGIC 
# MAGIC ## Summary
# MAGIC 
# MAGIC ✅ All dataset files uploaded to Unity Catalog volume  
# MAGIC ✅ Pipeline executed successfully (Bronze → Silver → Gold)  
# MAGIC ✅ All tables created and validated  
# MAGIC ✅ Sample queries ran successfully  
# MAGIC 
# MAGIC ## Next Steps
# MAGIC 
# MAGIC 1. **Explore the data** using the Catalog browser
# MAGIC 2. **Create dashboards** using Databricks SQL
# MAGIC 3. **Schedule the pipeline** as a Databricks Job
# MAGIC 4. **Share your work** with stakeholders
# MAGIC 
# MAGIC ## What You've Built
# MAGIC 
# MAGIC - **Medallion Architecture** with Bronze, Silver, and Gold layers
# MAGIC - **Unity Catalog** integration for data governance
# MAGIC - **Delta Lake** tables with ACID transactions
# MAGIC - **Structured Streaming** for incremental processing
# MAGIC - **Production-ready** data pipeline
# MAGIC 
# MAGIC **Congratulations! 🎊**

# COMMAND ----------


