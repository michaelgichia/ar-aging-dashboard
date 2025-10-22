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


## **Screenshots**
<img width="1703" height="694" alt="Screenshot 2025-10-22 at 18 33 10" src="https://github.com/user-attachments/assets/d9f0deba-a303-430e-bcf9-30ddf8abbc55" />
<img width="1908" height="543" alt="Screenshot 2025-10-22 at 18 34 49" src="https://github.com/user-attachments/assets/6e6fb9ab-8bae-4187-a50b-232a1562387f" />
<img width="1817" height="759" alt="Screenshot 2025-10-22 at 18 35 20" src="https://github.com/user-attachments/assets/3c670b1d-a5f1-42f1-94d8-cfb54b5fe4ea" />
<img width="1917" height="467" alt="Screenshot 2025-10-22 at 18 35 57" src="https://github.com/user-attachments/assets/f777b6e7-cb6e-4c87-9b65-8a4d6c41e489" />
