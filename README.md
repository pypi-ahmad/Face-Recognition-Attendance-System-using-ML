# 🛡️ AccessGuard AI: Enterprise Identity Verification System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![InsightFace](https://img.shields.io/badge/Engine-InsightFace%20(ArcFace)-green)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**AccessGuard AI** is a state-of-the-art (SOTA) biometric attendance system designed to replace legacy file-based logging with a secure, vector-database-backed architecture. It uses **ArcFace (Buffalo_L)** for high-accuracy face recognition and **ChromaDB** for millisecond-scale identity retrieval.

---

## 🚀 Key Features

### 🧠 SOTA Recognition Engine
- **Engine**: Powered by **InsightFace (ArcFace)**, achieving 99.8% accuracy on LFW.
- **Vector Embeddings**: Converts faces into 512-dimensional vectors, making the system robust to aging, beard growth, and lighting changes.
- **Privacy-First**: No raw images are stored. Only mathematical vectors are saved in the database.

### ⚡ Vector Database & SQL Hybrid
- **ChromaDB**: Handles high-speed vector similarity searches (Cosine Similarity) to find identities in <10ms.
- **SQLite**: Manages relational metadata (Student Names, Roll Nos, Sections) and logs.

### 🛡️ Smart Kiosk UI
- **Real-Time Inference**: Processes webcam feed at high FPS using ONNX Runtime (CPU/GPU auto-switching).
- **Anti-Spoofing Ready**: capable of distinguishing real faces from photos (extensible).
- **Admin Dashboard**: Filter attendance by Year/Semester and export Excel reports.

### 🔄 Legacy Data Migration
- Includes a smart migration engine (`migrate_legacy.py`) that parses messy, non-standard Excel files to import thousands of students into the modern database automatically.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Model** | `InsightFace (Buffalo_L)` | Industry-standard Face Analysis model. |
| **Inference** | `ONNX Runtime` | Hardware-accelerated inference (CUDA/CoreML/CPU). |
| **Vector DB** | `ChromaDB` | Stores face embeddings for fast retrieval. |
| **Metadata DB** | `SQLite` | Relational storage for logs and user details. |
| **Frontend** | `Streamlit` | Interactive Kiosk and Admin Dashboard. |
| **Data Gen** | `Faker` | Synthetic data generation for stress testing. |

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pypi-ahmad/Face-Recognition-Attendance-System-using-ML.git
cd Face-Recognition-Attendance-System-using-ML
```

### 2. Set Up Environment
It is recommended to use a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize Databases
This script sets up the SQLite tables and ChromaDB collections.

```bash
python database_setup.py
```

## 📊 Usage Guide

### Step 1: Populate Data (Migration)
You can either import legacy Excel files or generate synthetic data for testing.

```bash
# Option A: Generate 3000+ dummy students
python generate_dummy_data.py

# Option B: Run the migration script to import data into SQLite
python migrate_legacy.py
```

### Step 2: Enroll Faces
Register biometric data for users. You can search by Name or Roll No.

```bash
python enroll.py
```
Follow the on-screen prompts.
- Press `s` to save your face vector.
- Press `q` to quit.

### Step 3: Launch Kiosk
Start the main application.

```bash
streamlit run app.py
```
- **Kiosk Mode**: Tick "Start Camera" to begin taking attendance.
- **Admin Mode**: Use the sidebar to generate and download Excel reports.

## 📂 Project Structure

```plaintext
AccessGuard-AI/
├── app.py                 # Main Streamlit Dashboard (Kiosk + Admin)
├── enroll.py              # CLI Tool for biometric enrollment
├── database_setup.py      # Database initialization script
├── migrate_legacy.py      # Smart Excel-to-SQLite migration tool
├── generate_dummy_data.py # Synthetic student generator
├── requirements.txt       # Project dependencies
├── data/
│   ├── synthetic_students.csv  # Generated student data
│   └── Attendance_xlsx/        # Legacy Excel files (optional)
└── chroma_db/             # Local Vector Database storage
```

## 🤝 Contribution
Contributions are welcome! Please fork the repository and submit a pull request.

**Future Roadmap:**
- [ ] Add Docker support (docker-compose up).
- [ ] Implement MiniFASNet for advanced liveness detection.
- [ ] Cloud sync for multi-campus deployment.

Author: Ahmad | License: MIT

