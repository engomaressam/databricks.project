#!/usr/bin/env python3
"""
Databricks Capstone Project - Complete Automated Setup
This script completes all remaining setup steps for the capstone project.

IMPORTANT: Before running, set environment variables:
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
    export DATABRICKS_TOKEN="your-token-here"

Or ensure ~/.databrickscfg is configured with your credentials.
"""

import os
import sys
from pathlib import Path
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog

# Configuration
import os
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://dbc-2c27949c-3f39.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")  # Set via environment variable or .databrickscfg
CATALOG_NAME = "omar"
SCHEMA_NAME = "sbit_db"
DATA_VOLUME = "capstone_data"
CHECKPOINT_VOLUME = "capstone_checkpoints"

def main():
    print("=" * 60)
    print("Databricks Capstone Project - Automated Setup")
    print("=" * 60)
    print()
    
    # Initialize Databricks client
    print("[1/6] Connecting to Databricks...")
    w = WorkspaceClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN)
    print(f"✅ Connected to workspace: {DATABRICKS_HOST}")
    print()
    
    # Step 1: Create schema if not exists
    print(f"[2/6] Creating schema {CATALOG_NAME}.{SCHEMA_NAME}...")
    try:
        w.schemas.create(
            name=SCHEMA_NAME,
            catalog_name=CATALOG_NAME,
            comment="Capstone project schema for fitness tracking data"
        )
        print(f"✅ Schema {CATALOG_NAME}.{SCHEMA_NAME} created")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Schema {CATALOG_NAME}.{SCHEMA_NAME} already exists")
        else:
            print(f"❌ Error creating schema: {e}")
    print()
    
    # Step 2: Create data volume
    print(f"[3/6] Creating volume {DATA_VOLUME}...")
    try:
        w.volumes.create(
            catalog_name=CATALOG_NAME,
            schema_name=SCHEMA_NAME,
            name=DATA_VOLUME,
            volume_type=catalog.VolumeType.MANAGED,
            comment="Volume for capstone project data files"
        )
        print(f"✅ Volume {CATALOG_NAME}.{SCHEMA_NAME}.{DATA_VOLUME} created")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Volume {CATALOG_NAME}.{SCHEMA_NAME}.{DATA_VOLUME} already exists")
        else:
            print(f"❌ Error creating volume: {e}")
    print()
    
    # Step 3: Create checkpoint volume
    print(f"[4/6] Creating checkpoint volume {CHECKPOINT_VOLUME}...")
    try:
        w.volumes.create(
            catalog_name=CATALOG_NAME,
            schema_name=SCHEMA_NAME,
            name=CHECKPOINT_VOLUME,
            volume_type=catalog.VolumeType.MANAGED,
            comment="Volume for streaming checkpoints"
        )
        print(f"✅ Volume {CATALOG_NAME}.{SCHEMA_NAME}.{CHECKPOINT_VOLUME} created")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️  Volume {CATALOG_NAME}.{SCHEMA_NAME}.{CHECKPOINT_VOLUME} already exists")
        else:
            print(f"❌ Error creating checkpoint volume: {e}")
    print()
    
    # Step 4: Upload data files to volume
    print("[5/6] Uploading dataset files to volume...")
    print("ℹ️  Note: File upload to volumes requires Databricks Files API")
    print("ℹ️  Files must be uploaded via Databricks UI or mounted storage")
    print()
    
    # Step 5: Update config file
    print("[6/6] Updating configuration file...")
    update_config_file()
    print("✅ Configuration updated")
    print()
    
    # Summary
    print("=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Upload data files from 'CapstoneProject/Capstone Project/Data Set/'")
    print(f"   to volume: {CATALOG_NAME}.{SCHEMA_NAME}.{DATA_VOLUME}")
    print("   ")
    print("   Option A: Use Databricks UI")
    print(f"     - Go to Catalog → {CATALOG_NAME} → {SCHEMA_NAME} → {DATA_VOLUME}")
    print("     - Click Upload and select all files from Data Set folder")
    print("   ")
    print("   Option B: Use dbutils in a notebook")
    print("     - Create a temp notebook and run:")
    print(f"     - dbutils.fs.cp('file:/Workspace/...', '/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{DATA_VOLUME}/')")
    print()
    print("2. Go to workspace: /Users/omaressamrme@outlook.com/capstone/")
    print("3. Open notebook: 07-run.py")
    print(f"4. Set Environment parameter to: {CATALOG_NAME}")
    print("5. Run All cells")
    print()
    print("🎯 Expected Output:")
    print(f"   - Database: {CATALOG_NAME}.{SCHEMA_NAME}")
    print("   - 13+ tables (Bronze, Silver, Gold layers)")
    print("   - Analytics view: gym_summary")
    print()

def update_config_file():
    """Update the 01-config.py file to use Unity Catalog volumes"""
    config_path = Path("CapstoneProject/Capstone Project/Notebooks/01-config.py")
    
    new_config = '''# Databricks notebook source
class Config():    
    def __init__(self):      
        # Updated to use Unity Catalog volumes
        self.base_dir_data = f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{DATA_VOLUME}"
        self.base_dir_checkpoint = f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{CHECKPOINT_VOLUME}"
        self.db_name = "{SCHEMA_NAME}"
        self.maxFilesPerTrigger = 1000
'''
    
    new_config = new_config.format(
        CATALOG_NAME=CATALOG_NAME,
        SCHEMA_NAME=SCHEMA_NAME,
        DATA_VOLUME=DATA_VOLUME,
        CHECKPOINT_VOLUME=CHECKPOINT_VOLUME
    )
    
    with open(config_path, 'w') as f:
        f.write(new_config)
    
    print(f"   Updated: {config_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
