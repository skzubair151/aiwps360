# PART 2: BUSINESS LOGIC LAYER (COMPLETE - WITH PRICE)
from database import Database
from datetime import datetime, timedelta
import sqlite3

class ProductionManager:
    def __init__(self):
        self.db = Database()
    
    # ============================================
    # WAREHOUSE - PRODUCT MANAGEMENT
    # ============================================
    def add_product(self, product_name, unit='PCS'):
        if not product_name or product_name.strip() == '':
            return False, "Product name cannot be empty"
        product_name = product_name.strip().title()
        if self.db.add_product(product_name, unit):
            return True, f"✅ Product '{product_name}' added successfully!"
        else:
            return False, f"❌ Product '{product_name}' already exists!"
    
    def get_all_products(self):
        return self.db.get_all_products()
    
    def delete_product(self, product_name):
        if self.db.delete_product(product_name):
            return True, f"✅ Product '{product_name}' deleted!"
        return False, "❌ Failed to delete product"
    
    # ============================================
    # WAREHOUSE - SUPPLIER MANAGEMENT
    # ============================================
    def add_supplier(self, supplier_name, supplier_address='', contact_person='', phone=''):
        if not supplier_name or supplier_name.strip() == '':
            return False, "Supplier name cannot be empty"
        supplier_name = supplier_name.strip().title()
        if self.db.add_supplier(supplier_name, supplier_address, contact_person, phone):
            return True, f"✅ Supplier '{supplier_name}' added successfully!"
        else:
            return False, f"❌ Supplier '{supplier_name}' already exists!"

    def get_all_suppliers(self):
        return self.db.get_all_suppliers()

    def get_supplier_by_name(self, supplier_name):
        return self.db.get_supplier_by_name(supplier_name)

    def delete_supplier(self, supplier_name):
        if self.db.delete_supplier(supplier_name):
            return True, f"✅ Supplier '{supplier_name}' deleted!"
        return False, "❌ Failed to delete supplier"
    
    # ============================================
    # WAREHOUSE - RAW MATERIAL ENTRY (WITH PRICE)
    # ============================================
    def add_raw_material_entry(self, supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, price, received_by):
        if not supplier_name or supplier_name.strip() == '':
            return False, "Supplier name cannot be empty"
        if not invoice_number or invoice_number.strip() == '':
            return False, "Invoice number cannot be empty"
        if not item_name or item_name.strip() == '':
            return False, "Item name cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if price < 0:
            return False, "Price cannot be negative"
        if not received_by or received_by.strip() == '':
            return False, "Received by name cannot be empty"
        
        supplier_name = supplier_name.strip().title()
        item_name = item_name.strip().title()
        received_by = received_by.strip().title()
        
        self.db.add_raw_material_entry(supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, price, received_by)
        total_price = quantity * price
        return True, f"✅ {quantity} {unit} of {item_name} received from {supplier_name} at {price}/unit (Total: {total_price})"
    
    def get_raw_material_entries(self):
        return self.db.get_raw_material_entries()
    
    # ============================================
    # WAREHOUSE - STOCK
    # ============================================
    def get_warehouse_stock(self):
        stock = self.db.get_warehouse_stock()
        if not stock:
            return {
                'total_items': 0,
                'total_quantity': 0,
                'items': []
            }
        total_qty = sum(item[1] for item in stock)
        return {
            'total_items': len(stock),
            'total_quantity': total_qty,
            'items': stock
        }
    
    def get_item_quantity(self, item_name):
        return self.db.get_item_quantity(item_name)
    
    # ============================================
    # PRODUCTION - WAREHOUSE TO PRODUCTION (Transfer)
    # ============================================
    def transfer_to_production(self, item_name, quantity, unit, received_by, issued_by, transfer_date, remark=''):
        if not item_name or item_name.strip() == '':
            return False, "Item name cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not received_by or received_by.strip() == '':
            return False, "Received by name cannot be empty"
        if not issued_by or issued_by.strip() == '':
            return False, "Issued by name cannot be empty"
        
        item_name = item_name.strip().title()
        
        stock_result = self.db.get_item_quantity(item_name)
        if stock_result is None:
            available = 0
            unit_db = 'PCS'
        else:
            available, unit_db = stock_result
        
        if available < quantity:
            return False, f"❌ Not enough stock! Available: {available} {unit_db}, Requested: {quantity} {unit}"
        
        self.db.add_warehouse_to_production(item_name, quantity, unit, received_by.strip().title(), issued_by.strip().title(), transfer_date, remark)
        return True, f"✅ {quantity} {unit} of {item_name} transferred to production"
    
    def get_transfers_to_production(self):
        return self.db.get_warehouse_to_production()
    
    # ============================================
    # PRODUCTION - CHECKING
    # ============================================
    def add_checking_record(self, check_date, item_name, quantity, unit, checker_name, remark=''):
        if not item_name or item_name.strip() == '':
            return False, "Item name cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not checker_name or checker_name.strip() == '':
            return False, "Checker name cannot be empty"
        
        item_name = item_name.strip().title()
        checker_name = checker_name.strip().title()
        
        self.db.add_checking_record(check_date, item_name, quantity, unit, checker_name, remark)
        return True, f"✅ {quantity} {unit} of {item_name} checked by {checker_name}"
    
    def get_checking_records(self):
        return self.db.get_checking_records()
    
    # ============================================
    # PRODUCTION - ASSEMBLY
    # ============================================
    def add_assembly_record(self, assembly_date, assembler_name, quantity, unit='PCS', remark=''):
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not assembler_name or assembler_name.strip() == '':
            return False, "Assembler name cannot be empty"
        assembler_name = assembler_name.strip().title()
        self.db.add_assembly_record(assembly_date, assembler_name, quantity, unit, remark)
        return True, f"✅ {quantity} {unit} assembled by {assembler_name}"
    
    def get_assembly_records(self):
        return self.db.get_assembly_records()
    
    def delete_assembly_record(self, record_id):
        return self.db.delete_assembly_record(record_id)
    
    # ============================================
    # HR - EMPLOYEE MANAGEMENT
    # ============================================
    def add_employee(self, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path):
        if not full_name or full_name.strip() == '':
            return False, "Employee name cannot be empty"
        full_name = full_name.strip().title()
        employee_code = self.db.get_next_employee_code()
        self.db.add_employee(employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path)
        return True, f"✅ Employee '{full_name}' added with code {employee_code}"
    
    def get_all_employees(self):
        return self.db.get_all_employees()
    
    def get_employee_names(self):
        return self.db.get_employee_names()
    
    def delete_employee(self, employee_code):
        if self.db.delete_employee(employee_code):
            return True, f"✅ Employee '{employee_code}' deleted!"
        return False, "❌ Failed to delete employee"
    
    # ============================================
    # HR - ATTENDANCE
    # ============================================
    def add_attendance(self, attendance_date, employee_code, check_in_time, status='Present', remark=''):
        if not employee_code or employee_code.strip() == '':
            return False, "Employee code cannot be empty"
        if self.db.add_attendance(attendance_date, employee_code, check_in_time, status, remark):
            return True, f"✅ Attendance recorded for {employee_code}"
        else:
            return False, f"❌ Attendance already recorded for {employee_code} on this date"
    
    def get_attendance(self, date=None):
        return self.db.get_attendance(date)
    
    def get_today_attendance(self):
        return self.db.get_today_attendance()
    
    # ============================================
    # SYSTEM - LANGUAGE
    # ============================================
    def get_language(self):
        return self.db.get_language()
    
    def set_language(self, language):
        return self.db.set_language(language)
    
    # ============================================
    # REPORTS - TODAY'S ASSEMBLY
    # ============================================
    def get_today_assembly(self):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('production.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) FROM assembly_records WHERE assembly_date = ?", (today,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    
    # ============================================
    # SALES - CUSTOMERS
    # ============================================
    def add_customer(self, customer_name, email, phone, address, city, country):
        if not customer_name or customer_name.strip() == '':
            return False, "Customer name cannot be empty"
        customer_code = self.db.get_next_customer_code()
        customer_name = customer_name.strip().title()
        if self.db.add_customer(customer_code, customer_name, email, phone, address, city, country):
            return True, f"✅ Customer '{customer_name}' added with code {customer_code}"
        return False, "❌ Failed to add customer"

    def get_all_customers(self):
        return self.db.get_all_customers()

    def get_customer_by_code(self, customer_code):
        return self.db.get_customer_by_code(customer_code)

    def delete_customer(self, customer_code):
        if self.db.delete_customer(customer_code):
            return True, f"✅ Customer '{customer_code}' deleted!"
        return False, "❌ Failed to delete customer"

    # ============================================
    # SALES - ORDERS
    # ============================================
    def create_sales_order(self, customer_code, order_date, delivery_date, items, notes, created_by):
        if not customer_code:
            return False, "Customer code cannot be empty"
        if not items or len(items) == 0:
            return False, "At least one item is required"
        order_number = self.db.get_next_order_number()
        status = 'Pending'
        self.db.add_sales_order(order_number, customer_code, order_date, delivery_date, status, notes, created_by)
        total_amount = 0
        for item in items:
            item_name = item.get('item_name')
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total_price = quantity * unit_price
            total_amount += total_price
            self.db.add_sales_order_item(order_number, item_name, quantity, unit_price, total_price)
        self.db.update_order_total(order_number, total_amount)
        return True, f"✅ Order {order_number} created successfully!"

    def get_all_orders(self):
        return self.db.get_all_orders()

    def get_order_details(self, order_number):
        return self.db.get_order_by_number(order_number)

    def update_order_status(self, order_number, status):
        return self.db.update_order_status(order_number, status)

    def delete_order(self, order_number):
        return self.db.delete_order(order_number)

    # ============================================
    # SALES - INVOICES
    # ============================================
    def create_invoice(self, order_number, invoice_date, due_date, notes):
        order, items = self.db.get_order_by_number(order_number)
        if not order:
            return False, "Order not found"
        customer_code = order[2]
        total_amount = order[6]
        invoice_number = self.db.get_next_invoice_number()
        status = 'Unpaid'
        paid_amount = 0
        self.db.add_invoice(invoice_number, order_number, customer_code, invoice_date, due_date, total_amount, paid_amount, status, notes)
        self.db.update_order_status(order_number, 'Invoiced')
        return True, f"✅ Invoice {invoice_number} created successfully!"

    def get_all_invoices(self):
        return self.db.get_all_invoices()

    def record_payment(self, invoice_number, amount):
        return self.db.update_invoice_payment(invoice_number, amount)

    def get_invoice_by_number(self, invoice_number):
        return self.db.get_invoice_by_number(invoice_number)
    
    # ============================================
    # DELETE RECORDS
    # ============================================
    def delete_raw_material_entry(self, record_id):
        return self.db.delete_raw_material_entry(record_id)
    
    def delete_transfer_to_production(self, record_id):
        return self.db.delete_warehouse_to_production(record_id)
    
    def delete_checking_record(self, record_id):
        return self.db.delete_checking_record(record_id)