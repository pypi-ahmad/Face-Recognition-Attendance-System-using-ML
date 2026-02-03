import pandas as pd
import random
from faker import Faker
import uuid
import os

fake = Faker()

# Configuration
YEARS = ['1st', '2nd', '3rd', '4th']
SEMESTERS = {
    '1st': ['1sem', '2sem'],
    '2nd': ['3sem', '4sem'],
    '3rd': ['5sem', '6sem'],
    '4th': ['7sem', '8sem']
}
SECTIONS = ['IT1', 'IT2', 'CS1', 'CS2']
STUDENTS_PER_SECTION = 100  # Adjust as needed

data = []

print("🚀 Generating Synthetic Student Data...")

for year in YEARS:
    for sem in SEMESTERS[year]:
        for sec in SECTIONS:
            for _ in range(STUDENTS_PER_SECTION):
                # Generate realistic data
                name = fake.name()
                # Roll No format: 0827 + Year + Dept + Random (e.g., 0827IT171001)
                roll_no = f"0827{sec[:2]}{random.randint(10000, 99999)}"
                user_id = str(uuid.uuid4())
                
                data.append({
                    "user_id": user_id,
                    "name": name,
                    "roll_no": roll_no,
                    "academic_year": year,
                    "semester": sem,
                    "section": sec
                })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
os.makedirs("data", exist_ok=True)
csv_path = os.path.join("data", "synthetic_students.csv")
df.to_csv(csv_path, index=False)

print(f"✅ Successfully created {len(df)} students.")
print(f"📂 Saved to: {csv_path}")
print("   Columns: user_id, name, roll_no, academic_year, semester, section")