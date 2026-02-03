import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from database_setup import get_sqlite_connection, get_chroma_collection
import uuid
import onnxruntime

def get_optimal_providers():
    """
    Check what hardware is available to ONNX Runtime to avoid warnings.
    Returns a list of providers (e.g., ['CUDAExecutionProvider', 'CPUExecutionProvider'])
    """
    available = onnxruntime.get_available_providers()
    # Prioritize CUDA or CoreML (macOS) if available
    priority = ['CUDAExecutionProvider', 'CoreMLExecutionProvider', 'CPUExecutionProvider']
    # Filter to only use what is actually installed/working
    return [p for p in priority if p in available]

# Initialize FaceAnalysis with dynamic providers
providers = get_optimal_providers()
print(f"🚀 Running on: {providers[0]}") # Log for the user

app = FaceAnalysis(name='buffalo_l', providers=providers)
app.prepare(ctx_id=0, det_size=(640, 640))

def register_face(user_id, embedding):
    collection = get_chroma_collection()
    collection.upsert(
        ids=[user_id],
        embeddings=[embedding.tolist()],
        metadatas=[{"user_id": user_id}]
    )
    print("✅ Face embedding stored in ChromaDB.")

def enroll():
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    print("\n=== 🎓 Student Enrollment System ===")
    identifier = input("Enter Roll No (or Name to search): ").strip()
    
    # Try to find by Roll No
    cursor.execute("SELECT * FROM Users WHERE roll_no = ?", (identifier,))
    user = cursor.fetchone()
    
    if not user:
        # Try by Name
        cursor.execute("SELECT * FROM Users WHERE name LIKE ?", (f"%{identifier}%",))
        users = cursor.fetchall()
        if len(users) == 1:
            user = users[0]
        elif len(users) > 1:
            print(f"⚠️ Multiple users found for '{identifier}':")
            for u in users:
                print(f"   - {u['name']} (Roll: {u['roll_no']})")
            return
    
    if user:
        print(f"👤 User Found: {user['name']} | Roll: {user['roll_no']}")
        user_id = user['user_id']
        if input("Update face data? (y/n): ").lower() != 'y':
            return
    else:
        print("\n➕ Creating New User")
        name = input("   Name: ").strip()
        roll_no = identifier if identifier else input("   Roll No: ").strip()
        year = input("   Year (e.g. 2nd): ").strip()
        sem = input("   Semester (e.g. 3rd): ").strip()
        section = input("   Section (e.g. IT1): ").strip()
        
        user_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO Users (user_id, name, roll_no, academic_year, semester, section)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, roll_no, year, sem, section))
        conn.commit()
        print(f"   User created successfully.")

    # Capture Face
    cap = cv2.VideoCapture(0)
    print("\n📸 Webcam Active")
    print("   [S] Save Face")
    print("   [Q] Quit")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
            
        faces = app.get(frame)
        display_frame = frame.copy()
        
        # Visual Feedback
        if len(faces) == 1:
            color = (0, 255, 0) # Green (Good)
            status = "Ready to Enroll"
        else:
            color = (0, 0, 255) # Red (Bad)
            status = "Ensure 1 Face Visible"
            
        cv2.putText(display_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        for face in faces:
            box = face.bbox.astype(int)
            cv2.rectangle(display_frame, (box[0], box[1]), (box[2], box[3]), color, 2)
            
        cv2.imshow("Enrollment", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            if len(faces) == 1:
                embedding = faces[0].embedding
                register_face(user_id, embedding)
                print(f"\n🎉 Success! {name if 'name' in locals() else user['name']} is now enrolled.")
                break
            else:
                print("❌ Capture Failed: Exactly one face must be visible.")
        elif key == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    enroll()