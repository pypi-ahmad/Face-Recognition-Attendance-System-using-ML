import streamlit as st
import cv2
import numpy as np
import pandas as pd
from insightface.app import FaceAnalysis
from database_setup import get_sqlite_connection, get_chroma_collection
import time
from datetime import datetime

# Page Config
st.set_page_config(page_title="Attendance System", layout="wide")

# Cache resources
@st.cache_resource
def get_face_analyzer():
    app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app

@st.cache_resource
def get_chroma():
    return get_chroma_collection()

analyzer = get_face_analyzer()
collection = get_chroma()

# Sidebar - Admin Panel
st.sidebar.title("Admin Panel")
mode = st.sidebar.radio("Mode", ["Kiosk", "Reports"])

if mode == "Reports":
    st.title("Attendance Reports")
    
    conn = get_sqlite_connection()
    
    # Filters
    st.sidebar.subheader("Filters")
    
    # Get unique values for filters
    users_df = pd.read_sql("SELECT DISTINCT academic_year, semester, section FROM Users", conn)
    
    years = ["All"] + list(users_df['academic_year'].dropna().unique())
    sems = ["All"] + list(users_df['semester'].dropna().unique())
    sections = ["All"] + list(users_df['section'].dropna().unique())
    
    selected_year = st.sidebar.selectbox("Year", years)
    selected_sem = st.sidebar.selectbox("Semester", sems)
    selected_sec = st.sidebar.selectbox("Section", sections)
    
    query = """
    SELECT 
        u.name, u.roll_no, u.academic_year, u.semester, u.section, 
        a.timestamp, a.status, a.confidence_score
    FROM AttendanceLogs a
    JOIN Users u ON a.user_id = u.user_id
    WHERE 1=1
    """
    params = []
    
    if selected_year != "All":
        query += " AND u.academic_year = ?"
        params.append(selected_year)
    if selected_sem != "All":
        query += " AND u.semester = ?"
        params.append(selected_sem)
    if selected_sec != "All":
        query += " AND u.section = ?"
        params.append(selected_sec)
        
    query += " ORDER BY a.timestamp DESC"
    
    df_report = pd.read_sql(query, conn, params=params)
    
    st.dataframe(df_report)
    
    if not df_report.empty:
        st.download_button(
            "Download Excel",
            data=pd.io.formats.excel.ExcelFormatter(df_report), # This is tricky with streamlit button, need to save to buffer.
            file_name="attendance_report.xlsx"
        )
        # Fix download button for excel
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False)
            
        st.download_button(
            label="Download Excel Report",
            data=buffer.getvalue(),
            file_name="attendance_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    conn.close()

elif mode == "Kiosk":
    st.title("Live Attendance Kiosk")
    
    run = st.checkbox('Start Camera')
    FRAME_WINDOW = st.image([])
    status_text = st.empty()
    
    if run:
        cap = cv2.VideoCapture(0)
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        last_log_time = {} # user_id -> timestamp
        
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera not found")
                break
            
            # RGB conversion for Streamlit/InsightFace
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            faces = analyzer.get(img_rgb)
            
            for face in faces:
                box = face.bbox.astype(int)
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                
                embedding = face.embedding
                
                # Search ChromaDB
                results = collection.query(
                    query_embeddings=[embedding.tolist()],
                    n_results=1
                )
                
                if results['ids'] and results['ids'][0]:
                    # Check distance (Cosine distance: lower is better, < 0.5 usually good)
                    # Note: ChromaDB default distance might be L2 or Cosine depending on setup.
                    # I set metadata={"hnsw:space": "cosine"} in setup.
                    # Cosine distance ranges 0 to 2. 0 is identical.
                    
                    dist = results['distances'][0][0]
                    user_id = results['ids'][0][0]
                    
                    if dist < 0.5: # Threshold
                        # Fetch user name
                        cursor.execute("SELECT name, section FROM Users WHERE user_id = ?", (user_id,))
                        user_row = cursor.fetchone()
                        
                        if user_row:
                            name = user_row['name']
                            section = user_row['section']
                            
                            # Log if not logged recently (e.g. last 1 minute)
                            now = time.time()
                            if user_id not in last_log_time or (now - last_log_time[user_id] > 60):
                                cursor.execute('''
                                    INSERT INTO AttendanceLogs (user_id, timestamp, status, confidence_score)
                                    VALUES (?, ?, ?, ?)
                                ''', (user_id, datetime.now(), 'Present', 1 - dist))
                                conn.commit()
                                last_log_time[user_id] = now
                                status_text.success(f"Welcome {name} ({section}) - Marked Present!")
                            
                            cv2.putText(frame, f"{name} ({dist:.2f})", (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    else:
                        cv2.putText(frame, "Unknown", (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

            # Display
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Stop if checkbox unchecked (Streamlit rerun logic handles this largely)
        
        cap.release()
        conn.close()
    else:
        st.write("Click 'Start Camera' to begin.")
