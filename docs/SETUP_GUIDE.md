# Databricks Capstone Project - Setup Guide

## Completed Steps
1. Git repository cleaned and pushed (token secured)
2. Databricks CLI configured
3. All 10 notebooks imported to workspace: `/Users/omaressamrme@outlook.com/capstone/`

## Remaining Setup Steps

### Step 1: Create Unity Catalog Volume for Data Storage

Since your workspace uses Unity Catalog, we need to create a **Volume** to store data files.

**In Databricks UI:**

1. Go to **Catalog** → **omar** (your catalog)
2. Create a **Schema** if not exists: `sbit_db`
3. Click **Create** → **Volume**
   - **Name**: `capstone_data`
   - **Type**: **Managed**
4. Upload dataset files to this volume

**Alternative - Use CLI to create volume:**
```bash
# This will be automated in the next script
```

---

### Step 2: Create External Locations (Unity Catalog)

The project needs two external locations:

#### Option A: Use Managed Storage (Simpler - Recommended for Testing)
We'll modify the config to use Unity Catalog volumes instead of external locations.

#### Option B: Use External Storage (Production-like)
1. Go to **Catalog** → **External Data** → **External Locations**
2. Create two external locations:
   - **Name**: `data_zone`
     - **URL**: `abfss://data@yourstorage.dfs.core.windows.net/`
     - **Credential**: Select or create Azure storage credential
   
   - **Name**: `checkpoint`
     - **URL**: `abfss://checkpoints@yourstorage.dfs.core.windows.net/`
     - **Credential**: Same as above

**Note:** Requires Azure Storage Account with ADLS Gen2 enabled.

---

### Step 3: Upload Dataset Files

**Option 1 - Upload via Databricks UI:**
1. Go to **Catalog** → **omar** → **sbit_db** → **capstone_data**
2. Click **Upload** and select files from:
   - `CapstoneProject/Capstone Project/Data Set/`

**Option 2 - Use the automated script (next section)**

---

### Step 4: Modify Config for Volume-Based Storage

Update `01-config.py` to use volumes:

```python
class Config():    
    def __init__(self):      
        # Use Unity Catalog volumes instead of external locations
        self.base_dir_data = "/Volumes/omar/sbit_db/capstone_data"
        self.base_dir_checkpoint = "/Volumes/omar/sbit_db/capstone_checkpoints"
        self.db_name = "sbit_db"
        self.maxFilesPerTrigger = 1000
```

---

### Step 5: Create Checkpoint Volume

```sql
-- Run in Databricks SQL Editor
CREATE VOLUME IF NOT EXISTS omar.sbit_db.capstone_checkpoints;
```

---

### Step 6: Run the Pipeline

1. Go to workspace: `/Users/omaressamrme@outlook.com/capstone/`
2. Open notebook `07-run.py`
3. Update the widget parameter:
   - **Environment**: `omar` (your catalog name)
   - **RunType**: `once` (batch mode)
4. Click **Run All**

---

## Automated Setup (Next Steps)

I'll create a script to:
1. Create volumes automatically
2. Upload data files
3. Modify config file
4. Create a Databricks job to run the pipeline

**Ready to proceed with automated setup?**

---

## Expected Results

After successful execution:
- **Bronze Layer**: 3 tables with raw data
- **Silver Layer**: 8 curated tables
- **Gold Layer**: 2 analytics tables/views
- Total database: `omar.sbit_db` with ~13 tables

---

## Troubleshooting

**Token Permission Error:**
- Your token needs: `workspace`, `clusters`, `sql`, `unity-catalog` permissions
- Regenerate token with all scopes if needed

**External Location Not Found:**
- Use the volume-based approach (Option A) instead
- External locations require cloud storage setup

**Notebook Execution Fails:**
- Ensure catalog name in config matches: `omar`
- Check cluster has Unity Catalog enabled
- Verify compute permissions
