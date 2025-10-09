# Databricks Lakehouse Fitness Tracking Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Databricks](https://img.shields.io/badge/Databricks-Runtime%2014.3%20LTS-red)](https://databricks.com/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.0-green)](https://delta.io/)
[![Unity Catalog](https://img.shields.io/badge/Unity%20Catalog-Enabled-orange)](https://databricks.com/product/unity-catalog)

## Project Overview

A **production-ready data engineering pipeline** built on Databricks Lakehouse Platform, implementing the **Medallion Architecture** (Bronze/Silver/Gold) to process fitness tracking data from multiple sources (gym logins, heart rate monitors, workout sessions).

This project demonstrates enterprise-grade data engineering practices including:
- **Medallion Architecture** with multi-layer data processing
- **Unity Catalog** for data governance and lineage
- **Delta Lake** for ACID transactions and time travel
- **Structured Streaming** for incremental data processing
- **Schema evolution** and data quality validation
- **Automated orchestration** ready for production deployment

---

## Business Problem

**Fitness tracking company** needs to consolidate data from multiple systems:
- User registrations from mobile apps
- Gym check-in/check-out logs
- Real-time heart rate monitoring
- Workout session tracking
- User profile updates

**Goal**: Build a scalable data pipeline that:
1. Ingests data from heterogeneous sources (CSV, JSON, streaming)
2. Cleanses and standardizes data
3. Creates analytics-ready datasets
4. Enables real-time insights for health monitoring

---

## Architecture

### Medallion Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                 │
│  CSV Files  │  JSON Streams  │  Parquet  │  Kafka Topics       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BRONZE LAYER                                │
│  Raw Data Ingestion - Exact copy from source                    │
│  • registered_users_bz   • gym_logins_bz                        │
│  • kafka_multiplex_bz                                           │
│  Format: Delta Lake  │  Schema: Minimal validation              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SILVER LAYER                                │
│  Cleaned & Transformed - Business logic applied                 │
│  • users         • gym_logs        • user_profile               │
│  • heart_rate    • workouts        • completed_workouts         │
│  • workout_bpm   • user_bins       • date_lookup                │
│  Format: Delta Lake  │  Schema: Enforced & validated            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GOLD LAYER                                  │
│  Analytics-Ready - Aggregated for BI/ML                         │
│  • workout_bpm_summary  • gym_summary                           │
│  Format: Delta Lake Views  │  Optimized for queries             │
└─────────────────────────────────────────────────────────────────┘
```
### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Platform** | Databricks Lakehouse | Unified data platform |
| **Storage Format** | Delta Lake | ACID transactions, time travel |
| **Catalog** | Unity Catalog | Data governance, lineage |
| **Compute** | Spark 3.5+ | Distributed processing |
| **Language** | Python + SQL | Pipeline implementation |
| **Streaming** | Structured Streaming | Real-time data ingestion |
| **Version Control** | Git + GitHub | Code repository |

---

## Repository Structure

```
databricks.project/
├── README.md                   # This file
│
├── Notebooks/                    # Databricks notebooks
│   ├── 00-upload-data-helper.py    # Data ingestion helper
│   ├── 01-bronze-layer.py          # Bronze layer ingestion
│   ├── 02-silver-layer.py          # Silver transformations
│   ├── 03-gold-layer.py            # Gold analytics
│   ├── 07-run.py                   # Main pipeline orchestrator
│   └── FINAL-WORKING.py            # Complete all-in-one demo
│
├── FINAL-WORKING-Run1.ipynb     # Executed notebook with outputs
│
├── CapstoneProject/              # Dataset files
│   └── Capstone Project/
│       └── Data Set/               # Source data files (CSV/JSON/Parquet)
│
├── Documentation/
│   ├── README.md                   # This file
│   ├── ARCHITECTURE.md             # Detailed architecture guide
│   ├── SETUP_GUIDE.md              # Installation instructions
│   ├── PRESENTATION.md             # Executive summary for companies
│   └── PROJECT_STATUS.md           # Implementation checklist
│
├── Scripts/                     # Automation scripts
│   ├── setup-databricks.ps1       # Initial Databricks setup
│   ├── create_cluster.py          # Cluster provisioning
│   └── check_clusters.py          # Environment validation
│
├── Configuration/
│   ├── databricks.yml             # Databricks project config
│   ├── .databrickscfg             # Credentials (git ignored)
│   └── .gitignore                 # Git exclusions
│
└── Slides/                      # Presentation materials
    └── [PowerPoint presentations]
```