# End-to-End Enterprise Data Warehouse for Super-App Ecosystem

![Architecture Overview](https://img.shields.io/badge/Architecture-Galaxy_Schema-blue)
![Database](https://img.shields.io/badge/OLAP-ClickHouse-yellow)
![Database](https://img.shields.io/badge/OLTP-PostgreSQL-blue)
![ETL](https://img.shields.io/badge/ETL-Python-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)

A comprehensive data engineering project simulating the extraction, transformation, and analytical serving of highly fragmented transactional data from a multi-vertical super-app ecosystem (inspired by Gojek). 

This project demonstrates how to transition from normalized operational databases (OLTP) to a high-performance denormalized analytical environment (OLAP) capable of delivering sub-second query latency for complex Business Intelligence dashboards.

---

## 📖 Project Overview

In a typical super-app environment, transactional data is siloed across multiple service verticals (e.g., Ride-hailing, Food delivery, Logistics, Digital Payments). Running cross-vertical analytical queries directly on these highly normalized (3NF) operational databases causes severe performance degradation.

**The Solution:** 
This project builds an Enterprise Data Warehouse (EDW) that completely isolates analytical workloads from the operational layer. By implementing a **Kimball bottom-up dimensional model (Galaxy Schema)** inside a columnar database (**ClickHouse**), the system enables complex multidimensional queries with near-instantaneous response times.

## 🏗️ System Architecture

The project consists of 4 distinct layers:

1. **Operational Layer (OLTP)**: A Flutter-based data generator simulates user transactions across 4 verticals (GoRide, GoFood, GoSend, GoPay) and feeds them into a normalized PostgreSQL database (hosted on Supabase).
2. **Integration Layer (ETL)**: A custom Python-based orchestrator utilizing Pandas to Extract, Transform, and Load (ETL) data. It performs rigorous data cleansing and manages Slowly Changing Dimensions (SCD Type 2) tracking.
3. **Analytical Layer (OLAP)**: The core data warehouse powered by ClickHouse. It utilizes `MergeTree` engines, temporal partitioning (`toYYYYMM`), and Materialized Views for automatic pre-aggregation.
4. **Presentation Layer**: A FastAPI backend serves the aggregated ClickHouse data via REST endpoints, which are consumed and visualized by a highly interactive Next.js dashboard.

---

## 🌌 Data Modeling: Galaxy Schema (Fact Constellation)

To enable cross-vertical analysis (e.g., correlating digital wallet usage with food delivery demand), the data warehouse employs a **Galaxy Schema** architecture consisting of:

*   **4 Fact Tables**: `fact_gofood`, `fact_goride`, `fact_gosend`, `fact_gopay`
*   **8 Conformed Dimensions**: `dim_user`, `dim_merchant`, `dim_driver`, `dim_location`, `dim_promo`, `dim_payment_method`, `dim_date`, `dim_status`

---

## 📂 Repository Structure

```text
📦 GojekDataWarehouse
 ┣ 📂 datwer-gojek-project
 ┃ ┣ 📂 backend           # Python ETL pipeline, FastAPI backend, ClickHouse schema
 ┃ ┗ 📂 frontend          # Next.js interactive dashboard UI
 ┣ 📂 gojek_dummy_generator # Flutter app to simulate operational OLTP transactions
 ┣ 📂 MISC                # Academic papers, ERD diagrams, and documentation
 ┗ 📜 README.md
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
*   Python 3.9+
*   Node.js 18+ & npm
*   Flutter SDK (for the data generator)
*   ClickHouse Server (Local or Cloud)
*   PostgreSQL / Supabase (Operational Database)

### 2. Environment Setup
You must create a `.env` file in the root of both the `backend` and `frontend` directories.
*   **Backend `.env`**: Needs credentials for PostgreSQL (Supabase) and ClickHouse.
*   **Frontend `.env`**: Needs the API base URL pointing to the FastAPI backend.

### 3. Running the Backend (ETL & API)
Open a terminal and navigate to the backend directory:
```bash
cd datwer-gojek-project/backend
pip install -r requirements.txt

# To run the ETL Pipeline manually:
python -m src.etl.orchestrator

# To run the FastAPI server (serving data to the frontend):
uvicorn src.api.main:app --reload --port 8000
```

### 4. Running the Frontend (Next.js Dashboard)
Open a second terminal and navigate to the frontend directory:
```bash
cd datwer-gojek-project/frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:3000`.

### 5. Running the Data Generator (Flutter)
Open a third terminal and navigate to the Flutter directory to generate dummy transactions:
```bash
cd gojek_dummy_generator
flutter pub get
flutter run -d windows  # or -d chrome
```

---

## 📄 Academic Research
This project architecture is the subject of an academic paper titled: **"Designing an Enterprise Data Warehouse for Super-App Ecosystems: A Galaxy Schema Implementation for Gojek"**. The full paper detailing the research methodologies and performance benchmarks is available in the `MISC/` directory.
