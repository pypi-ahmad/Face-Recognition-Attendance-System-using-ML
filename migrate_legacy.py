import os
import pandas as pd
from database_setup import get_sqlite_connection, init_db

SYNTHETIC_DATA_PATH = os.path.join("data", "synthetic_students.csv")

def migrate():
    print(f"🚀 Starting Migration from: {SYNTHETIC_DATA_PATH}")
    
    if not os.path.exists(SYNTHETIC_DATA_PATH):
        print(f"❌ File not found! Run 'generate_dummy_data.py' first.")
        return

    # Initialize DB
    init_db()
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Load Clean Data
    df = pd.read_csv(SYNTHETIC_DATA_PATH)
    total = len(df)
    print(f"🔍 Found {total} records to import.")

    count = 0
    for _, row in df.iterrows():
        try:
            # Check if user exists (by Roll No)
            cursor.execute("SELECT user_id FROM Users WHERE roll_no = ?", (row['roll_no'],))
            existing = cursor.fetchone()

            if existing:
                # Update
                cursor.execute('''
                    UPDATE Users 
                    SET name=?, academic_year=?, semester=?, section=?
                    WHERE roll_no=?
                ''', (row['name'], row['academic_year'], row['semester'], row['section'], row['roll_no']))
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO Users (user_id, name, roll_no, academic_year, semester, section)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['user_id'], row['name'], row['roll_no'], row['academic_year'], row['semester'], row['section']))
            
            count += 1
            if count % 100 == 0:
                print(f"   ... imported {count}/{total}")

        except Exception as e:
            print(f"❌ Error importing {row['name']}: {e}")

    conn.commit()
    conn.close()
    print(f"\n🎉 Migration Complete! {count} students added/updated in the database.")

if __name__ == "__main__":
    migrate()