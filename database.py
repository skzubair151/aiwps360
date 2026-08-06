# PART 1: DATABASE LAYER (COMPLETE - WITH USERS + SALES MODULE)
import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_name='production.db'):
        self.db_name = db_name
        self.create_tables()
        self.insert_default_data()
    
    def create_tables(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # ============================================
        # WAREHOUSE TABLES
        # ============================================
        
        # 1. Products Master List
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE NOT NULL,
                unit TEXT DEFAULT 'PCS',
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        ''')
        
        # 2. Suppliers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT UNIQUE NOT NULL,
                supplier_address TEXT,
                contact_person TEXT,
                phone TEXT,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        ''')
        
        # 3. Raw Material Entry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_material_entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL,
                supplier_address TEXT,
                entry_date TEXT NOT NULL,
                invoice_number TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                received_by TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. Warehouse Stock
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit TEXT DEFAULT 'PCS',
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ============================================
        # PRODUCTION TABLES
        # ============================================
        
        # 5. Warehouse to Production Transfer
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_to_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                received_by TEXT NOT NULL,
                issued_by TEXT NOT NULL,
                transfer_date TEXT NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 6. Checking Records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checking_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                checker_name TEXT NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 7. Assembly Records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assembly_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assembly_date TEXT NOT NULL,
                assembler_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT DEFAULT 'PCS',
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 8. Packing Before Seal (LOT Created)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packing_before_seal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pack_date TEXT NOT NULL,
                packer_name TEXT NOT NULL,
                lot_number TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 9. Sealing Records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sealing_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seal_date TEXT NOT NULL,
                sealer_name TEXT NOT NULL,
                lot_number TEXT NOT NULL,
                sealing_qty INTEGER NOT NULL,
                packing_qty INTEGER NOT NULL,
                unit TEXT DEFAULT 'PCS',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_number) REFERENCES packing_before_seal(lot_number)
            )
        ''')
        
        # 10. Sterilization Entry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sterilization_entry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL,
                person_name TEXT NOT NULL,
                bag_quantity INTEGER NOT NULL,
                pcs_quantity INTEGER NOT NULL,
                lot_number TEXT NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_number) REFERENCES sealing_records(lot_number)
            )
        ''')
        
        # 11. Sterilization Start
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sterilization_start (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_datetime TEXT NOT NULL,
                operator_name TEXT NOT NULL,
                bag_quantity INTEGER NOT NULL,
                pcs_quantity INTEGER NOT NULL,
                lot_number TEXT NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_number) REFERENCES sterilization_entry(lot_number)
            )
        ''')
        
        # 12. Sterilization Finish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sterilization_finish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finish_datetime TEXT NOT NULL,
                operator_name TEXT NOT NULL,
                bag_quantity INTEGER NOT NULL,
                pcs_quantity INTEGER NOT NULL,
                lot_number TEXT NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_number) REFERENCES sterilization_start(lot_number)
            )
        ''')
        
        # 13. Packing After Sterilization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packing_after_sterile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pack_date TEXT NOT NULL,
                packer_name TEXT NOT NULL,
                lot_number TEXT NOT NULL,
                bag_quantity INTEGER NOT NULL,
                pcs_quantity INTEGER NOT NULL,
                remark TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_number) REFERENCES sterilization_finish(lot_number)
            )
        ''')
        
        # ============================================
        # HR MANAGEMENT TABLES
        # ============================================
        
        # 14. Employees
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
        
        # 15. Attendance
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
        
        # ============================================
        # SYSTEM TABLES
        # ============================================
        
        # 16. Language Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL
            )
        ''')
        
        # 17. Employee Code Counter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_number INTEGER DEFAULT 0
            )
        ''')
        
        # ============================================
        # USERS TABLE
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'Staff',
                status TEXT DEFAULT 'Active',
                created_date TEXT NOT NULL,
                last_login DATETIME
            )
        ''')
        
        # ============================================
        # SALES MODULE TABLES
        # ============================================
        
        # 18. Customers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                country TEXT,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        ''')
        
        # 19. Sales Orders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                customer_code TEXT NOT NULL,
                order_date TEXT NOT NULL,
                delivery_date TEXT,
                status TEXT DEFAULT 'Pending',
                total_amount REAL DEFAULT 0,
                notes TEXT,
                created_by TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code)
            )
        ''')
        
        # 20. Sales Order Items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_number) REFERENCES sales_orders(order_number)
            )
        ''')
        
        # 21. Invoices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                order_number TEXT NOT NULL,
                customer_code TEXT NOT NULL,
                invoice_date TEXT NOT NULL,
                due_date TEXT,
                total_amount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'Unpaid',
                notes TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_number) REFERENCES sales_orders(order_number),
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code)
            )
        ''')
        
        # 22. Customer Counter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_number INTEGER DEFAULT 0
            )
        ''')
        
        # 23. Order Counter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_number INTEGER DEFAULT 0
            )
        ''')
        
        # 24. Invoice Counter
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_number INTEGER DEFAULT 0
            )
        ''')
        
        # Insert default settings
        cursor.execute("INSERT OR IGNORE INTO system_settings (setting_key, setting_value) VALUES ('language', 'EN')")
        cursor.execute("INSERT OR IGNORE INTO employee_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO customer_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO order_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO invoice_counter (id, last_number) VALUES (1, 0)")
        
        conn.commit()
        conn.close()
    
    def insert_default_data(self):
        """Insert default data if tables are empty"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Default products
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            default_products = [
                'Chamber', 'Needle 35mm', 'Needle 39mm', 'Latex', 
                'Roller', 'Tub', 'Single Pack Poly', 'Multi Pack Poly'
            ]
            for product in default_products:
                cursor.execute(
                    "INSERT INTO products (product_name, created_date) VALUES (?, ?)",
                    (product, today)
                )
        
        # Insert default stock entries
        for product in ['Chamber', 'Needle 35mm', 'Needle 39mm', 'Latex', 'Roller', 'Tub', 'Single Pack Poly', 'Multi Pack Poly']:
            cursor.execute(
                "INSERT OR IGNORE INTO warehouse_stock (item_name, quantity, unit) VALUES (?, 0, 'PCS')",
                (product,)
            )
        
        # Default admin user
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            hashed = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, created_date) VALUES (?, ?, ?, ?, ?)",
                ('admin', hashed, 'Administrator', 'Admin', today)
            )
        
        # Default counters
        cursor.execute("INSERT OR IGNORE INTO employee_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO customer_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO order_counter (id, last_number) VALUES (1, 0)")
        cursor.execute("INSERT OR IGNORE INTO invoice_counter (id, last_number) VALUES (1, 0)")
        
        conn.commit()
        conn.close()
    
    # ============================================
    # USER MANAGEMENT
    # ============================================
    def add_user(self, username, password, full_name, role='Staff'):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, created_date) VALUES (?, ?, ?, ?, ?)",
                (username, password, full_name, role, today)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, status, last_login FROM users ORDER BY username")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_user(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    
    def update_user_role(self, username, role):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
        conn.commit()
        conn.close()
        return True
    
    def update_user_status(self, username, status):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
        conn.commit()
        conn.close()
        return True
    
    def update_last_login(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_user(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    # ============================================
    # PRODUCTS
    # ============================================
    def add_product(self, product_name, unit='PCS'):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO products (product_name, unit, created_date) VALUES (?, ?, ?)",
                (product_name, unit, today)
            )
            cursor.execute(
                "INSERT INTO warehouse_stock (item_name, quantity, unit) VALUES (?, 0, ?)",
                (product_name, unit)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_all_products(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, unit FROM products WHERE status = 'Active' ORDER BY product_name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_product(self, product_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_name = ?", (product_name,))
        conn.commit()
        conn.close()
        return True
    
    # ============================================
    # SUPPLIERS
    # ============================================
    def add_supplier(self, supplier_name, supplier_address='', contact_person='', phone=''):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO suppliers (supplier_name, supplier_address, contact_person, phone, created_date) VALUES (?, ?, ?, ?, ?)",
                (supplier_name, supplier_address, contact_person, phone, today)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_all_suppliers(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, supplier_name, supplier_address, contact_person, phone FROM suppliers WHERE status = 'Active' ORDER BY supplier_name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_supplier_by_name(self, supplier_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_name, supplier_address, contact_person, phone FROM suppliers WHERE supplier_name = ?", (supplier_name,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def delete_supplier(self, supplier_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE supplier_name = ?", (supplier_name,))
        conn.commit()
        conn.close()
        return True
    
    # ============================================
    # RAW MATERIAL
    # ============================================
    def add_raw_material_entry(self, supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raw_material_entry (supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by)
        )
        cursor.execute('''
            INSERT INTO warehouse_stock (item_name, quantity, unit) 
            VALUES (?, ?, ?) 
            ON CONFLICT(item_name) 
            DO UPDATE SET quantity = quantity + ?, unit = ?
        ''', (item_name, quantity, unit, quantity, unit))
        conn.commit()
        conn.close()
        return True
    
    def get_raw_material_entries(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by FROM raw_material_entry ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # WAREHOUSE STOCK
    # ============================================
    def get_warehouse_stock(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity, unit FROM warehouse_stock ORDER BY item_name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_item_quantity(self, item_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, unit FROM warehouse_stock WHERE item_name = ?", (item_name,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (0, 'PCS')
    
    def deduct_warehouse_stock(self, item_name, quantity):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE warehouse_stock SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE item_name = ?",
            (quantity, item_name)
        )
        conn.commit()
        conn.close()
    
    # ============================================
    # PRODUCTION - TRANSFER
    # ============================================
    def add_warehouse_to_production(self, item_name, quantity, unit, received_by, issued_by, transfer_date, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO warehouse_to_production (item_name, quantity, unit, received_by, issued_by, transfer_date, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item_name, quantity, unit, received_by, issued_by, transfer_date, remark)
        )
        cursor.execute(
            "UPDATE warehouse_stock SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE item_name = ?",
            (quantity, item_name)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_warehouse_to_production(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_name, quantity, unit, received_by, issued_by, transfer_date, remark FROM warehouse_to_production ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # PRODUCTION - CHECKING
    # ============================================
    def add_checking_record(self, check_date, item_name, quantity, unit, checker_name, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO checking_records (check_date, item_name, quantity, unit, checker_name, remark) VALUES (?, ?, ?, ?, ?, ?)",
            (check_date, item_name, quantity, unit, checker_name, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_checking_records(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, check_date, item_name, quantity, unit, checker_name, remark FROM checking_records ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # PRODUCTION - ASSEMBLY
    # ============================================
    def add_assembly_record(self, assembly_date, assembler_name, quantity, unit='PCS', remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assembly_records (assembly_date, assembler_name, quantity, unit, remark) VALUES (?, ?, ?, ?, ?)",
            (assembly_date, assembler_name, quantity, unit, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_assembly_records(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, assembly_date, assembler_name, quantity, unit, remark FROM assembly_records ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_today_assembly(self):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) FROM assembly_records WHERE assembly_date = ?", (today,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    
    # ============================================
    # PRODUCTION - PACKING BEFORE SEAL
    # ============================================
    def add_packing_before_seal(self, pack_date, packer_name, lot_number, quantity, unit):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO packing_before_seal (pack_date, packer_name, lot_number, quantity, unit) VALUES (?, ?, ?, ?, ?)",
            (pack_date, packer_name, lot_number, quantity, unit)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_packing_before_seal(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, pack_date, packer_name, lot_number, quantity, unit FROM packing_before_seal ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_lot_numbers(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT lot_number FROM packing_before_seal ORDER BY lot_number")
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]
    
    def get_lot_info(self, lot_number):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT pack_date, packer_name, quantity, unit FROM packing_before_seal WHERE lot_number = ?", (lot_number,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    # ============================================
    # PRODUCTION - SEALING
    # ============================================
    def add_sealing_record(self, seal_date, sealer_name, lot_number, sealing_qty, packing_qty):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sealing_records (seal_date, sealer_name, lot_number, sealing_qty, packing_qty) VALUES (?, ?, ?, ?, ?)",
            (seal_date, sealer_name, lot_number, sealing_qty, packing_qty)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_sealing_records(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, seal_date, sealer_name, lot_number, sealing_qty, packing_qty FROM sealing_records ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # PRODUCTION - STERILIZATION
    # ============================================
    def add_sterilization_entry(self, entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sterilization_entry (entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark) VALUES (?, ?, ?, ?, ?, ?)",
            (entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_sterilization_entries(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark FROM sterilization_entry ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def add_sterilization_start(self, start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sterilization_start (start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark) VALUES (?, ?, ?, ?, ?, ?)",
            (start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def add_sterilization_finish(self, finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sterilization_finish (finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark) VALUES (?, ?, ?, ?, ?, ?)",
            (finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_sterilization_starts(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark FROM sterilization_start ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_sterilization_finishes(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark FROM sterilization_finish ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # PRODUCTION - PACKING AFTER STERILE
    # ============================================
    def add_packing_after_sterile(self, pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO packing_after_sterile (pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark) VALUES (?, ?, ?, ?, ?, ?)",
            (pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_packing_after_sterile(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark FROM packing_after_sterile ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ============================================
    # HR - EMPLOYEES
    # ============================================
    def get_next_employee_code(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE employee_counter SET last_number = last_number + 1 WHERE id = 1")
        cursor.execute("SELECT last_number FROM employee_counter WHERE id = 1")
        next_num = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return f"A{next_num:02d}"
    
    def add_employee(self, employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO employees (employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path, today)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_all_employees(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path FROM employees WHERE status = 'Active' ORDER BY full_name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_employee_names(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT employee_code, full_name FROM employees WHERE status = 'Active' ORDER BY full_name")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_employee(self, employee_code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE employee_code = ?", (employee_code,))
        conn.commit()
        conn.close()
        return True
    
    # ============================================
    # HR - ATTENDANCE
    # ============================================
    def add_attendance(self, attendance_date, employee_code, check_in_time, status='Present', remark=''):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO attendance (attendance_date, employee_code, check_in_time, status, remark) VALUES (?, ?, ?, ?, ?)",
                (attendance_date, employee_code, check_in_time, status, remark)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_attendance(self, date=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if date:
            cursor.execute(
                "SELECT a.attendance_date, e.full_name, a.check_in_time, a.status, a.remark FROM attendance a JOIN employees e ON a.employee_code = e.employee_code WHERE a.attendance_date = ? ORDER BY e.full_name",
                (date,)
            )
        else:
            cursor.execute("SELECT a.attendance_date, e.full_name, a.check_in_time, a.status, a.remark FROM attendance a JOIN employees e ON a.employee_code = e.employee_code ORDER BY a.attendance_date DESC")
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_attendance(today)
    
    # ============================================
    # SYSTEM - LANGUAGE
    # ============================================
    def get_language(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'language'")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'EN'
    
    def set_language(self, language):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_settings SET setting_value = ? WHERE setting_key = 'language'", (language,))
        conn.commit()
        conn.close()
        return True
    
    # ============================================
    # REPORTS
    # ============================================
    def get_sterilized_goods_report(self):
        finishes = self.get_sterilization_finishes()
        total_bags = sum(f[3] for f in finishes) if finishes else 0
        total_pcs = sum(f[4] for f in finishes) if finishes else 0
        return {'total_bags': total_bags, 'total_pcs': total_pcs, 'records': finishes}
    
    # ============================================
    # SALES - CUSTOMERS
    # ============================================
    def get_next_customer_code(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE customer_counter SET last_number = last_number + 1 WHERE id = 1")
        cursor.execute("SELECT last_number FROM customer_counter WHERE id = 1")
        next_num = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return f"C{next_num:04d}"

    def add_customer(self, customer_code, customer_name, email, phone, address, city, country):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers (customer_code, customer_name, email, phone, address, city, country, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (customer_code, customer_name, email, phone, address, city, country, today)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    def get_all_customers(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_code, customer_name, email, phone, address, city, country, created_date FROM customers WHERE status = 'Active' ORDER BY customer_name")
        results = cursor.fetchall()
        conn.close()
        return results

    def get_customer_by_code(self, customer_code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_code, customer_name, email, phone, address, city, country FROM customers WHERE customer_code = ?", (customer_code,))
        result = cursor.fetchone()
        conn.close()
        return result

    def delete_customer(self, customer_code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE customer_code = ?", (customer_code,))
        conn.commit()
        conn.close()
        return True

    # ============================================
    # SALES - ORDERS
    # ============================================
    def get_next_order_number(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE order_counter SET last_number = last_number + 1 WHERE id = 1")
        cursor.execute("SELECT last_number FROM order_counter WHERE id = 1")
        next_num = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return f"SO{next_num:05d}"

    def add_sales_order(self, order_number, customer_code, order_date, delivery_date, status, notes, created_by):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales_orders (order_number, customer_code, order_date, delivery_date, status, notes, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_number, customer_code, order_date, delivery_date, status, notes, created_by)
        )
        conn.commit()
        conn.close()
        return True

    def add_sales_order_item(self, order_number, item_name, quantity, unit_price, total_price):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales_order_items (order_number, item_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
            (order_number, item_name, quantity, unit_price, total_price)
        )
        conn.commit()
        conn.close()
        return True

    def update_order_total(self, order_number, total_amount):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sales_orders SET total_amount = ? WHERE order_number = ?",
            (total_amount, order_number)
        )
        conn.commit()
        conn.close()
        return True

    def get_all_orders(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.order_number, c.customer_name, o.order_date, o.delivery_date, o.status, o.total_amount, o.notes 
            FROM sales_orders o 
            JOIN customers c ON o.customer_code = c.customer_code 
            ORDER BY o.timestamp DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_order_by_number(self, order_number):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales_orders WHERE order_number = ?", (order_number,))
        order = cursor.fetchone()
        if order:
            cursor.execute("SELECT item_name, quantity, unit_price, total_price FROM sales_order_items WHERE order_number = ?", (order_number,))
            items = cursor.fetchall()
            conn.close()
            return order, items
        conn.close()
        return None, None

    def update_order_status(self, order_number, status):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sales_orders SET status = ? WHERE order_number = ?",
            (status, order_number)
        )
        conn.commit()
        conn.close()
        return True

    def delete_order(self, order_number):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sales_order_items WHERE order_number = ?", (order_number,))
        cursor.execute("DELETE FROM sales_orders WHERE order_number = ?", (order_number,))
        conn.commit()
        conn.close()
        return True

    # ============================================
    # SALES - INVOICES
    # ============================================
    def get_next_invoice_number(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE invoice_counter SET last_number = last_number + 1 WHERE id = 1")
        cursor.execute("SELECT last_number FROM invoice_counter WHERE id = 1")
        next_num = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return f"INV{next_num:05d}"

    def add_invoice(self, invoice_number, order_number, customer_code, invoice_date, due_date, total_amount, paid_amount, status, notes):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (invoice_number, order_number, customer_code, invoice_date, due_date, total_amount, paid_amount, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (invoice_number, order_number, customer_code, invoice_date, due_date, total_amount, paid_amount, status, notes)
        )
        conn.commit()
        conn.close()
        return True

    def get_all_invoices(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.invoice_number, i.order_number, c.customer_name, i.invoice_date, i.due_date, i.total_amount, i.paid_amount, i.status 
            FROM invoices i 
            JOIN customers c ON i.customer_code = c.customer_code 
            ORDER BY i.timestamp DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def update_invoice_payment(self, invoice_number, paid_amount):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE invoices SET paid_amount = paid_amount + ?, status = CASE WHEN paid_amount + ? >= total_amount THEN 'Paid' ELSE 'Partial' END WHERE invoice_number = ?",
            (paid_amount, paid_amount, invoice_number)
        )
        conn.commit()
        conn.close()
        return True

    def get_invoice_by_number(self, invoice_number):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
        result = cursor.fetchone()
        conn.close()
        return result

    # ============================================
    # DELETE RECORDS
    # ============================================
    def delete_raw_material_entry(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw_material_entry WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_warehouse_to_production(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warehouse_to_production WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_checking_record(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checking_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_assembly_record(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assembly_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_packing_before_seal(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM packing_before_seal WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_sealing_record(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sealing_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_sterilization_entry(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sterilization_entry WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_packing_after_sterile(self, record_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM packing_after_sterile WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True