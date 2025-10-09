# How to Create All-Purpose Cluster in Databricks

## The Confusion: SQL Warehouses vs Clusters

You're currently looking at **SQL Warehouses** which are different from **All-Purpose Clusters**.

- **SQL Warehouses**: For SQL queries only
- **All-Purpose Clusters**: For Python notebooks, Spark jobs, etc.

---

## Finding the Cluster Creation Page

### Option A: Direct URL

Go directly to:
```
https://dbc-2c27949c-3f39.cloud.databricks.com/#setting/clusters
```

### Option B: Through UI

1. Click **"Compute"** in left sidebar
2. Look for tabs at the top - you might see:
   - **"All-Purpose Clusters"** or **"Clusters"**
   - "SQL Warehouses" (where you are now)
   - "Instance Pools"
   - "Apps"

3. Click on **"All-Purpose Clusters"** or **"Clusters"** tab

4. You should see a **"Create Cluster"** button

---

## Alternative: Use Workspace Notebooks Menu

1. Go to **Workspace** → **Users** → **omaressamrme@outlook.com** → **capstone**
2. Open the **`INSTANT-COMPLETE`** notebook
3. At the top, click the **cluster dropdown** (where it says "Detached" or "Connect")
4. Click **"Start new cluster"** or **"Create new cluster"**
5. This will open cluster creation directly from the notebook

---

## Cluster Settings (When You Find It)

When you create the cluster, use these settings:

- **Cluster Name**: `Capstone-Cluster`
- **Policy**: None (or default)
- **Access Mode**: **Single User** ⚠️ (CRITICAL!)
- **Databricks Runtime**: **14.3 LTS** or newer
- **Node Type**: Default is fine
- **Number of Workers**: 1 (minimum)
- **Terminate after**: 120 minutes of inactivity

Click **Create Cluster**

---

## If You Still Can't Find It

Try these:

### 1. Check the Hamburger Menu
Sometimes there's a ☰ menu that expands to show "Clusters"

### 2. Search Bar
Use the search at the top of Databricks and type "cluster"

### 3. New Compute Experience
If your workspace uses the new UI, try:
- Click **Compute** → Look for a **"+ Create"** button
- Or look for tabs like "Compute", "SQL Warehouses", "Jobs"

---

## Screenshot Help

Your current screen shows SQL Warehouses. You need to navigate AWAY from this tab to find the all-purpose clusters section.

Look for additional tabs or menu items near "SQL Warehouses".
