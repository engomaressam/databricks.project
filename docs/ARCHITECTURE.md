# System Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Medallion Architecture](#medallion-architecture)
3. [Data Flow](#data-flow)
4. [Schema Design](#schema-design)
5. [Technology Decisions](#technology-decisions)
6. [Performance Optimizations](#performance-optimizations)

---

## Overview

This project implements a **Lakehouse Architecture** using Databricks platform, following the industry-standard **Medallion pattern** (Bronze/Silver/Gold layers) for data processing.

### Core Principles

- **Single Source of Truth**: All data in Delta Lake format
- **Data Quality by Design**: Validation at each layer
- **Scalability First**: Built to handle growth
- **Governance Enabled**: Unity Catalog from day one

---

## Medallion Architecture

### Bronze Layer: Raw Data Preservation

**Purpose**: Ingest and store raw data exactly as received from sources.

**Characteristics**:
- Minimal transformations (only add metadata)
- Schema-on-read approach
- Full data lineage
- Immutable audit trail

**Tables**:

| Table | Source | Format | Purpose |
|-------|--------|--------|---------|
| `registered_users_bz` | Mobile app CSV | Delta | User registrations |
| `gym_logins_bz` | Access system CSV | Delta | Gym check-ins/outs |
| `kafka_multiplex_bz` | Kafka topics JSON | Delta | Streaming data (profiles, BPM, workouts) |

**Schema Pattern**:
```sql
CREATE TABLE bronze_table (
    -- Original source columns (preserved as-is)
    ...,
    
    -- Audit columns (added)
    load_time TIMESTAMP,
    source_file STRING
)
```

### Silver Layer: Curated Data

**Purpose**: Clean, validate, and transform data into business-ready format.

**Transformations Applied**:
1. **Type Casting**: String → appropriate types (int, timestamp, etc.)
2. **Deduplication**: Remove exact duplicates
3. **Normalization**: Split nested JSON into separate tables
4. **Validation**: Check for nulls, ranges, referential integrity
5. **Enrichment**: Add derived fields (e.g., age from DOB)

**Tables**:

| Table | Source | Key Transformations |
|-------|--------|-------------------|
| `users` | registered_users_bz | Type cast, dedupe on user_id |
| `gym_logs` | gym_logins_bz | Timestamp conversion, MAC lookup |
| `user_profile` | kafka_multiplex_bz | JSON parsing, address normalization |
| `heart_rate` | kafka_multiplex_bz | Device→user mapping, BPM validation |
| `workouts` | kafka_multiplex_bz | Session extraction, type classification |
| `completed_workouts` | workouts | Start/stop matching, duration calc |
| `workout_bpm` | workouts + heart_rate | Time-window join |
| `date_lookup` | Generated | Calendar dimension with week/year |

**Schema Pattern**:
```sql
CREATE TABLE silver_table (
    -- Business keys
    business_id BIGINT PRIMARY KEY,
    
    -- Attributes (typed correctly)
    attribute1 STRING,
    attribute2 TIMESTAMP,
    ...,
    
    -- No audit columns (clean business view)
) USING DELTA
```

### Gold Layer: Analytics-Ready Aggregations

**Purpose**: Pre-compute metrics and KPIs for fast BI queries.

**Design**:
- Denormalized (star schema)
- Pre-aggregated
- Optimized for read performance
- Often materialized as views for flexibility

**Views/Tables**:

| Object | Type | Business Question | Key Metrics |
|--------|------|-------------------|-------------|
| `gym_summary` | VIEW | How long do users spend at gyms? | date, gym, mac_address, minutes_in_gym |
| `workout_bpm_summary` | TABLE | What's the avg heart rate during workouts? | session_id, user_id, workout_type, avg_bpm, min_bpm, max_bpm, duration |

**Schema Pattern**:
```sql
CREATE OR REPLACE VIEW gold_view AS
SELECT 
    dimension1,
    dimension2,
    AGGREGATE(metric1) as aggregated_metric,
    ...
FROM silver_tables
GROUP BY dimension1, dimension2
```

---

## Data Flow

### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ EXTERNAL SOURCES                                                │
│                                                                 │
│ [Mobile App] → CSV → DBFS/Volume                               │
│ [Gym Access] → CSV → DBFS/Volume                              │
│ [Wearables]  → JSON → Kafka → DBFS/Volume                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ BRONZE LAYER - Raw Ingestion                                   │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐       │
│ │ registered_ │  │ gym_logins_ │  │ kafka_multiplex_ │       │
│ │ users_bz    │  │ bz          │  │ bz               │       │
│ └─────────────┘  └─────────────┘  └──────────────────┘       │
│                                                                 │
│ • spark.read() from source                                     │
│ • .withColumn("load_time", current_timestamp())                │
│ • .write.format("delta").save()                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ SILVER LAYER - Transformation                                  │
│                                                                 │
│ ┌──────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐      │
│ │users │  │gym_logs  │  │user_profile │  │heart_rate  │      │
│ └──────┘  └──────────┘  └─────────────┘  └────────────┘      │
│                                                                 │
│ ┌─────────┐  ┌─────────────────┐  ┌────────────┐             │
│ │workouts │  │completed_workouts│  │workout_bpm │             │
│ └─────────┘  └─────────────────┘  └────────────┘             │
│                                                                 │
│ • Cast types                                                    │
│ • Remove duplicates                                             │
│ • Apply business rules                                          │
│ • Join related data                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ GOLD LAYER - Analytics                                         │
│                                                                 │
│ ┌──────────────┐       ┌──────────────────────┐               │
│ │ gym_summary  │       │ workout_bpm_summary  │               │
│ │  (VIEW)      │       │  (TABLE)             │               │
│ └──────────────┘       └──────────────────────┘               │
│                                                                 │
│ • Pre-aggregated metrics                                        │
│ • Optimized for BI tools                                        │
│ • Denormalized for performance                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ CONSUMPTION LAYER                                               │
│                                                                 │
│ • Databricks SQL Dashboards                                     │
│ • Power BI / Tableau                                            │
│ • ML Models (Feature Engineering)                               │
│ • REST API (Query Federation)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Processing Modes

**Batch Processing** (Current implementation):
- Processes entire dataset each run
- Simple, reliable
- Good for historical data

**Streaming Processing** (Future enhancement):
- Structured Streaming API
- Checkpoint-based progress tracking
- Exactly-once delivery semantics
- Low-latency (seconds)

---

## Schema Design

### Users (Silver Layer)

```sql
CREATE TABLE omar.sbit_db.users (
    user_id BIGINT NOT NULL,          -- Primary key
    device_id BIGINT NOT NULL,        -- Wearable device ID
    mac_address STRING NOT NULL,      -- Gym access ID
    registration_timestamp TIMESTAMP  -- When user signed up
) USING DELTA
```

**Business Rules**:
- `user_id` must be unique (enforced by deduplication)
- `mac_address` links to gym_logs
- `device_id` links to heart_rate

### Gym Logs (Silver Layer)

```sql
CREATE TABLE omar.sbit_db.gym_logs (
    mac_address STRING NOT NULL,      -- Foreign key to users
    gym BIGINT NOT NULL,              -- Gym location ID (1-5)
    login TIMESTAMP NOT NULL,         -- Check-in time
    logout TIMESTAMP NOT NULL         -- Check-out time
) USING DELTA
```

**Business Rules**:
- `logout` > `login` (validated in transformation)
- Duration = logout - login
- One record per gym visit

### Workout BPM Summary (Gold Layer)

```sql
CREATE OR REPLACE VIEW omar.sbit_db.workout_bpm_summary AS
SELECT
    session_id,
    user_id,
    workout_id,
    workout_name,
    avg(heartrate) as avg_bpm,
    min(heartrate) as min_bpm,
    max(heartrate) as max_bpm,
    count(*) as total_measurements,
    (max(time) - min(time)) / 60 as duration_minutes
FROM workout_bpm
GROUP BY session_id, user_id, workout_id, workout_name
```

**Business Value**:
- Identifies workout intensity
- Detects anomalies (unusual heart rates)
- Enables personalized recommendations

---

## Technology Decisions

### Why Databricks?

| Requirement | Databricks Solution | Benefit |
|-------------|-------------------|---------|
| Unified platform | Lakehouse architecture | No data silos |
| Scale | Apache Spark + Cloud | Handle TB→PB growth |
| Governance | Unity Catalog | Enterprise-ready |
| Performance | Delta Lake + caching | Fast queries |
| Real-time | Structured Streaming | Low latency |
| ML | MLflow + AutoML | Integrated AI |

### Why Delta Lake?

**ACID Transactions**:
- Concurrent reads/writes without corruption
- Rollback on failure

**Time Travel**:
```sql
-- Query data as it was yesterday
SELECT * FROM users VERSION AS OF 5
SELECT * FROM users TIMESTAMP AS OF '2024-01-01'
```

**Schema Evolution**:
```sql
-- Add column without rewriting data
ALTER TABLE users ADD COLUMN age INT
```

**Optimized Storage**:
- Automatic file compaction
- Z-ordering for faster queries
- Statistics for query optimization

### Why Unity Catalog?

**3-Level Namespace**:
- `catalog.schema.table` (vs 2-level `database.table`)
- Centralized metadata across workspaces

**Data Lineage**:
- Automatic tracking (which table created from what)
- Regulatory compliance

**Access Control**:
```sql
GRANT SELECT ON TABLE omar.sbit_db.users TO `data_analysts`
REVOKE SELECT ON COLUMN omar.sbit_db.users.email FROM `external_users`
```

---

## Performance Optimizations

### 1. Partitioning

**kafka_multiplex_bz** partitioned by `(topic, week_part)`:

```sql
CREATE TABLE kafka_multiplex_bz (
    ...
) PARTITIONED BY (topic, week_part)
```

**Benefit**: Query only relevant partitions
```sql
-- Only scans workout partition
SELECT * FROM kafka_multiplex_bz WHERE topic = 'workout'
```

### 2. Z-Ordering

```sql
OPTIMIZE omar.sbit_db.users ZORDER BY (user_id)
OPTIMIZE omar.sbit_db.gym_logs ZORDER BY (mac_address, login)
```

**Benefit**: Co-locate related data for faster filtering

### 3. Caching

```sql
-- Cache frequently accessed table
CACHE TABLE omar.sbit_db.date_lookup
```

**Benefit**: Sub-second query times for repeated access

### 4. Broadcast Joins

Small dimension tables (< 10MB) automatically broadcast:
```python
# Spark broadcasts date_lookup automatically
df = workout_bpm.join(date_lookup, on="date")
```

**Benefit**: Avoid shuffle for small tables

### 5. Predicate Pushdown

Delta Lake reads only necessary columns and rows:
```sql
-- Only reads mac_address column and gym=1 rows
SELECT mac_address FROM gym_logs WHERE gym = 1
```

---

## Scalability Considerations

### Current Scale
- **Data Volume**: 500+ records
- **Cluster**: 2 workers (minimal)
- **Execution**: ~7 minutes end-to-end

### Production Scale Estimates

| Metric | Current | 1 Year | 5 Years |
|--------|---------|--------|---------|
| **Users** | 10 | 100K | 1M |
| **Daily BPM Records** | 100 | 10M | 100M |
| **Data Volume** | 1 MB | 100 GB | 10 TB |
| **Cluster Size** | 2 nodes | 10 nodes | 50 nodes |
| **Cost/Month** | $50 | $500 | $5K |

### Scaling Strategy

1. **Horizontal Scaling**: Add more workers (Spark auto-distributes)
2. **Partitioning**: Partition by date for time-series queries
3. **Compaction**: Regular OPTIMIZE to merge small files
4. **Caching**: Cache hot data in cluster memory
5. **Auto-Loader**: Use for efficient incremental ingestion
6. **Photon Engine**: Enable for 2-3x query speedup

---

## Monitoring & Observability

### Built-in Metrics

**Databricks UI provides**:
- Query execution plans (Spark UI)
- Resource utilization (CPU, memory)
- Data skew detection
- Cache hit rates

### Logging

Each notebook logs:
```python
print(f"Loaded {count} records into {table_name}")
```

### Data Quality Checks

```python
assert df.count() > 0, "Empty dataframe!"
assert df.select("user_id").distinct().count() == df.count(), "Duplicate user_ids!"
```

---

## Security Architecture

### Data at Rest
- **Encryption**: AES-256 (Cloud provider default)
- **Access**: Unity Catalog permissions

### Data in Transit
- **HTTPS**: All Databricks APIs
- **TLS 1.2**: Inter-node communication

### Authentication
- **Databricks**: OAuth 2.0 or PAT tokens
- **Unity Catalog**: SCIM integration with Azure AD/Okta

### Authorization
```sql
-- Row-level security
CREATE ROW ACCESS POLICY user_data_policy
    AS (user_id) -> user_id = current_user()

ALTER TABLE users SET ROW FILTER user_data_policy ON (user_id)
```

---

## Disaster Recovery

### Backup Strategy

**Delta Lake benefits**:
- All data versioned (automatic history)
- Can restore to any previous state
- No additional backup needed

**Checkpoints**:
- Streaming checkpoints in separate volume
- Replay from checkpoint on failure

### Recovery Procedures

**Scenario 1: Bad data loaded**
```sql
-- Rollback table to previous version
RESTORE TABLE users TO VERSION AS OF 10
```

**Scenario 2: Accidental table drop**
```sql
-- Restore from metadata (if not purged)
UNDROP TABLE users
```

**Scenario 3: Corruption**
- Re-run pipeline from Bronze layer
- Bronze is immutable, can always reprocess

---

## Future Architecture Enhancements

### Phase 2: Real-time Streaming

```python
# Replace batch read with streaming
df = spark.readStream \
    .format("delta") \
    .table("registered_users_bz")

# Write with checkpoint
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", checkpoint_path) \
    .table("users")
```

### Phase 3: Machine Learning

```
Silver Layer → Feature Store → ML Models → Gold Layer
```

- Use `workout_bpm_summary` as features
- Predict workout recommendations
- Detect health anomalies

### Phase 4: Data Mesh

- Decentralize by domain (users, workouts, gyms)
- Each domain owns its pipelines
- Shared governance via Unity Catalog

---

## Conclusion

This architecture demonstrates:
- Industry-standard patterns (Medallion)
- Production-ready technologies (Databricks, Delta Lake)
- Scalability from MVP to enterprise
- Security and governance built-in
- Performance optimizations applied

**Next Steps**: Deploy to production with Databricks Workflows, add monitoring, implement streaming.

---

*Last Updated: January 2025*
*Author: Omar Essam*
