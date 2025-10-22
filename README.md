# **AR Aging Dashboard **

## **Project Overview**

This repository hosts the PoC for developing a dynamic, real-time **Accounts Receivable (AR) Aging Dashboard**.

The dashboard will analyze outstanding customer invoices, categorize them by time buckets, and surface essential data for risk assessment and business decision-making.

## **Technical Scope and Objectives**
### **Key Deliverables:**

1. **Data Ingestion:** Ingest sample Customer, Invoice, and Payment data from the Unified.to Sandbox API.  
2. **Data Transformation (ETL/ELT):**  
   * Calculate and bucket outstanding invoices into standard AR aging categories: **Current, 31–60, 61–90, 91–120, and 120+ days past due.**  
   * Orchestrate the Extract-Transform-Load (ETL) flow using **Dagster**.  
3. **Data Persistence:** Load all processed and structured data into a **PostgreSQL** database instance.  
4. **Dashboard Views:** functional dashboard views:  


### **Technology Stack:**

| Category | Technology | Purpose in PoC |
| :---- | :---- | :---- |
| **Backend Framework** | **Django** | Serving the application and handling logic. |
| **Frontend/Interactivity** | **Jinja** | Lightweight, modern interactivity layer. |
| **ETL Orchestration** | **Dagster** | Defining and running the data pipeline (Ingest, Transform, Load). |
| **Database** | **PostgreSQL** | Persistent, structured data storage. |
| **Data Source** | **Unified.to Sandbox** | API connectivity layer for QuickBooks sample data. |
