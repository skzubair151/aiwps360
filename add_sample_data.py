# add_sample_data.py
import sqlite3
from datetime import datetime
import hashlib

def add_sample_data():
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    
    # ============================================
    # FIRST: ADD MISSING COLUMNS TO USERS TABLE
    # ============================================
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add missing columns if they don't exist
    if 'email' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("✅ Added 'email' column")
    
    if 'phone' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        print("✅ Added 'phone' column")
    
    if 'department' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")
        print("✅ Added 'department' column")
    
    if 'can_manage_users' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN can_manage_users INTEGER DEFAULT 0")
        print("✅ Added 'can_manage_users' column")
    
    if 'can_manage_accounts' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN can_manage_accounts INTEGER DEFAULT 0")
        print("✅ Added 'can_manage_accounts' column")
    
    if 'can_view_reports' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN can_view_reports INTEGER DEFAULT 1")
        print("✅ Added 'can_view_reports' column")
    
    # ============================================
    # CREATE TABLES IF NOT EXISTS
    # ============================================
    
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            national_id TEXT,
            mobile1 TEXT,
            mobile2 TEXT,
            address TEXT,
            blood_group TEXT,
            picture_path TEXT,
            status TEXT DEFAULT 'Active',
            created_date TEXT NOT NULL
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_date TEXT NOT NULL,
            employee_code TEXT NOT NULL,
            check_in_time TEXT,
            status TEXT DEFAULT 'Present',
            remark TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_code) REFERENCES employees(employee_code),
            UNIQUE(attendance_date, employee_code)
        )
    ''')
    
    # Employee counter
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_counter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_number INTEGER DEFAULT 0
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO employee_counter (id, last_number) VALUES (1, 0)")
    
    # ============================================
    # INSERT SAMPLE EMPLOYEES
    # ============================================
    
    # Clear existing employees
    cursor.execute("DELETE FROM employees")
    
    employees = [
        ('A01', 'John Smith', 'ID001', '+996700111111', '+996700111112', 'Bishkek, Chui 123', 'A+'),
        ('A02', 'Jane Doe', 'ID002', '+996700222222', '+996700222223', 'Bishkek, Manas 456', 'B+'),
        ('A03', 'Bob Johnson', 'ID003', '+996700333333', '+996700333334', 'Bishkek, Kievskaya 789', 'O+'),
        ('A04', 'Alice Williams', 'ID004', '+996700444444', '+996700444445', 'Bishkek, Bokonbaeva 321', 'AB+'),
        ('A05', 'Charlie Brown', 'ID005', '+996700555555', '+996700555556', 'Bishkek, Orozbekova 654', 'A-'),
        ('A06', 'David Miller', 'ID006', '+996700666666', '+996700666667', 'Bishkek, Tynystanova 987', 'B-'),
        ('A07', 'Emma Wilson', 'ID007', '+996700777777', '+996700777778', 'Bishkek, Abdymomunova 159', 'O-'),
        ('A08', 'Frank Davis', 'ID008', '+996700888888', '+996700888889', 'Bishkek, Jibek Jolu 753', 'AB-'),
        ('A09', 'Grace Taylor', 'ID009', '+996700999999', '+996700999900', 'Bishkek, Moskovskaya 246', 'A+'),
        ('A10', 'Henry Moore', 'ID010', '+996700101010', '+996700101011', 'Bishkek, Almatinskaya 357', 'B+'),
    ]
    
    today = datetime.now().strftime('%Y-%m-%d')
    for emp in employees:
        cursor.execute('''
            INSERT OR REPLACE INTO employees 
            (employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6], '', today))
    
    print(f"✅ Added {len(employees)} employees")
    
    # ============================================
    # INSERT SAMPLE ATTENDANCE
    # ============================================
    
    # Clear existing attendance
    cursor.execute("DELETE FROM attendance")
    
    today = datetime.now().strftime('%Y-%m-%d')
    attendance_records = [
        (today, 'A01', '09:00:00', 'Present', ''),
        (today, 'A02', '09:15:00', 'Present', ''),
        (today, 'A03', '10:00:00', 'Present', 'Traffic delay'),
        (today, 'A04', '08:45:00', 'Present', ''),
        (today, 'A05', '09:30:00', 'Present', ''),
        (today, 'A06', '09:20:00', 'Present', ''),
        (today, 'A07', '08:50:00', 'Present', ''),
        (today, 'A08', '10:30:00', 'Present', ''),
        (today, 'A09', '09:10:00', 'Present', ''),
        (today, 'A10', '08:55:00', 'Present', ''),
    ]
    
    for att in attendance_records:
        cursor.execute('''
            INSERT OR IGNORE INTO attendance 
            (attendance_date, employee_code, check_in_time, status, remark)
            VALUES (?, ?, ?, ?, ?)
        ''', att)
    
    print(f"✅ Added {len(attendance_records)} attendance records")
    
    # ============================================
    # INSERT SAMPLE USERS (WITH NEW COLUMNS)
    # ============================================
    
    # Clear existing users (keep admin)
    cursor.execute("DELETE FROM users")
    
    today = datetime.now().strftime('%Y-%m-%d')
    users = [
        # username, password, full_name, role, user_type, email, phone, department, can_manage_users, can_manage_accounts, can_view_reports
        ('admin', 'admin123', 'System Administrator', 'Admin', 'Admin', 'admin@aiwps.com', '+996700000000', 'IT', 1, 1, 1),
        ('manager', 'manager123', 'Manager User', 'Manager', 'Admin', 'manager@aiwps.com', '+996700000001', 'Management', 1, 1, 1),
        ('hr_manager', 'hr123', 'HR Manager', 'Manager', 'Admin', 'hr@aiwps.com', '+996700000002', 'HR', 1, 0, 1),
        ('operator', 'operator123', 'Operator User', 'Staff', 'Viewer', 'operator@aiwps.com', '+996700000003', 'Production', 0, 0, 1),
        ('viewer', 'viewer123', 'Viewer User', 'Staff', 'Viewer', 'viewer@aiwps.com', '+996700000004', 'Sales', 0, 0, 1),
        ('warehouse', 'warehouse123', 'Warehouse Staff', 'Staff', 'Viewer', 'warehouse@aiwps.com', '+996700000005', 'Warehouse', 0, 0, 1),
        ('quality', 'quality123', 'Quality Control', 'Staff', 'Viewer', 'quality@aiwps.com', '+996700000006', 'Quality', 0, 0, 1),
    ]
    
    for user in users:
        hashed = hashlib.sha256(user[1].encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users 
            (username, password, full_name, role, created_date, user_type, email, phone, department, 
             can_manage_users, can_manage_accounts, can_view_reports, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
        ''', (user[0], hashed, user[2], user[3], today, user[4], user[5], user[6], user[7], 
              user[8], user[9], user[10]))
    
    print(f"✅ Added {len(users)} sample users")
    
    # ============================================
    # COMMIT AND CLOSE
    # ============================================
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("🎉 SAMPLE DATA ADDED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 EMPLOYEES:")
    print("  10 employees added (A01 - A10)")
    print("\n📋 ATTENDANCE:")
    print("  10 attendance records for today")
    print("\n📋 USERS:")
    print("  admin / admin123 (Admin)")
    print("  manager / manager123 (Manager)")
    print("  hr_manager / hr123 (HR Manager)")
    print("  operator / operator123 (Operator)")
    print("  viewer / viewer123 (Viewer)")
    print("  warehouse / warehouse123 (Warehouse)")
    print("  quality / quality123 (Quality Control)")
    print("="*50)

if __name__ == '__main__':
    add_sample_data()