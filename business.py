# PART 2: BUSINESS LOGIC LAYER (COMPLETE - WITH SALES MODULE)
from database import Database
from datetime import datetime, timedelta

class ProductionManager:
    def __init__(self):
        self.db = Database()
    
    # ============================================
    # WAREHOUSE - PRODUCT MANAGEMENT
    # ============================================
    def add_product(self, product_name, unit='PCS'):
        """Add a new product"""
        if not product_name or product_name.strip() == '':
            return False, "Product name cannot be empty"
        
        product_name = product_name.strip().title()
        
        if self.db.add_product(product_name, unit):
            return True, f"✅ Product '{product_name}' added successfully!"
        else:
            return False, f"❌ Product '{product_name}' already exists!"
    
    def get_all_products(self):
        """Get all products"""
        return self.db.get_all_products()
    
    def delete_product(self, product_name):
        """Delete a product"""
        if self.db.delete_product(product_name):
            return True, f"✅ Product '{product_name}' deleted!"
        return False, "❌ Failed to delete product"
    
    # ============================================
    # WAREHOUSE - SUPPLIER MANAGEMENT
    # ============================================
    def add_supplier(self, supplier_name, supplier_address='', contact_person='', phone=''):
        """Add a new supplier"""
        if not supplier_name or supplier_name.strip() == '':
            return False, "Supplier name cannot be empty"
        
        supplier_name = supplier_name.strip().title()
        
        if self.db.add_supplier(supplier_name, supplier_address, contact_person, phone):
            return True, f"✅ Supplier '{supplier_name}' added successfully!"
        else:
            return False, f"❌ Supplier '{supplier_name}' already exists!"

    def get_all_suppliers(self):
        """Get all suppliers"""
        return self.db.get_all_suppliers()

    def get_supplier_by_name(self, supplier_name):
        """Get supplier details by name"""
        return self.db.get_supplier_by_name(supplier_name)

    def delete_supplier(self, supplier_name):
        """Delete a supplier"""
        if self.db.delete_supplier(supplier_name):
            return True, f"✅ Supplier '{supplier_name}' deleted!"
        return False, "❌ Failed to delete supplier"
    
    # ============================================
    # WAREHOUSE - RAW MATERIAL ENTRY
    # ============================================
    def add_raw_material_entry(self, supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by):
        """Record raw materials from supplier to warehouse"""
        if not supplier_name or supplier_name.strip() == '':
            return False, "Supplier name cannot be empty"
        if not invoice_number or invoice_number.strip() == '':
            return False, "Invoice number cannot be empty"
        if not item_name or item_name.strip() == '':
            return False, "Item name cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not received_by or received_by.strip() == '':
            return False, "Received by name cannot be empty"
        
        supplier_name = supplier_name.strip().title()
        item_name = item_name.strip().title()
        received_by = received_by.strip().title()
        
        self.db.add_raw_material_entry(supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by)
        return True, f"✅ {quantity} {unit} of {item_name} received from {supplier_name}"
    
    def get_raw_material_entries(self):
        """Get all raw material entries"""
        return self.db.get_raw_material_entries()
    
    # ============================================
    # WAREHOUSE - STOCK
    # ============================================
    def get_warehouse_stock(self):
        """Get all warehouse stock"""
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
        """Get current quantity of an item"""
        return self.db.get_item_quantity(item_name)
    
    # ============================================
    # PRODUCTION - WAREHOUSE TO PRODUCTION
    # ============================================
    def transfer_to_production(self, item_name, quantity, unit, received_by, issued_by, transfer_date, remark=''):
        """Transfer materials from warehouse to production"""
        if not item_name or item_name.strip() == '':
            return False, "Item name cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not received_by or received_by.strip() == '':
            return False, "Received by name cannot be empty"
        if not issued_by or issued_by.strip() == '':
            return False, "Issued by name cannot be empty"
        
        item_name = item_name.strip().title()
        
        available, unit_db = self.db.get_item_quantity(item_name)
        if available < quantity:
            return False, f"❌ Not enough stock! Available: {available} {unit_db}, Requested: {quantity} {unit}"
        
        self.db.add_warehouse_to_production(item_name, quantity, unit, received_by.strip().title(), issued_by.strip().title(), transfer_date, remark)
        return True, f"✅ {quantity} {unit} of {item_name} transferred to production"
    
    def get_transfers_to_production(self):
        """Get all transfers to production"""
        return self.db.get_warehouse_to_production()
    
    # ============================================
    # PRODUCTION - CHECKING
    # ============================================
    def add_checking_record(self, check_date, item_name, quantity, unit, checker_name, remark=''):
        """Record checking of materials"""
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
        """Get all checking records"""
        return self.db.get_checking_records()
    
    # ============================================
    # PRODUCTION - ASSEMBLY
    # ============================================
    def add_assembly_record(self, assembly_date, assembler_name, quantity, unit='PCS', remark=''):
        """Record assembly"""
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not assembler_name or assembler_name.strip() == '':
            return False, "Assembler name cannot be empty"
        
        assembler_name = assembler_name.strip().title()
        
        self.db.add_assembly_record(assembly_date, assembler_name, quantity, unit, remark)
        return True, f"✅ {quantity} {unit} assembled by {assembler_name}"
    
    def get_assembly_records(self):
        """Get all assembly records"""
        return self.db.get_assembly_records()
    
    def get_today_assembly(self):
        """Get today's assembly total"""
        return self.db.get_today_assembly()
    
    # ============================================
    # PRODUCTION - PACKING BEFORE SEAL (LOT CREATED)
    # ============================================
    def add_packing_before_seal(self, pack_date, packer_name, lot_number, quantity, unit):
        """Record packing before sealing - LOT created here"""
        if not packer_name or packer_name.strip() == '':
            return False, "Packer name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        packer_name = packer_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        self.db.add_packing_before_seal(pack_date, packer_name, lot_number, quantity, unit)
        return True, f"✅ LOT {lot_number} created: {quantity} {unit} packed by {packer_name}"
    
    def get_packing_before_seal(self):
        """Get all packing before seal records"""
        return self.db.get_packing_before_seal()
    
    def get_all_lot_numbers(self):
        """Get all lot numbers"""
        return self.db.get_all_lot_numbers()
    
    def get_lot_info(self, lot_number):
        """Get lot information"""
        return self.db.get_lot_info(lot_number)
    
    # ============================================
    # PRODUCTION - SEALING
    # ============================================
    def add_sealing_record(self, seal_date, sealer_name, lot_number, sealing_qty, packing_qty):
        """Record sealing"""
        if not sealer_name or sealer_name.strip() == '':
            return False, "Sealer name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        if sealing_qty <= 0:
            return False, "Sealing quantity must be greater than 0"
        if packing_qty <= 0:
            return False, "Packing quantity must be greater than 0"
        
        sealer_name = sealer_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        lot_info = self.db.get_lot_info(lot_number)
        if not lot_info:
            return False, f"❌ Lot number '{lot_number}' not found!"
        
        self.db.add_sealing_record(seal_date, sealer_name, lot_number, sealing_qty, packing_qty)
        return True, f"✅ LOT {lot_number}: {sealing_qty} sealed by {sealer_name}"
    
    def get_sealing_records(self):
        """Get all sealing records"""
        return self.db.get_sealing_records()
    
    # ============================================
    # PRODUCTION - STERILIZATION
    # ============================================
    def add_sterilization_entry(self, entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        """Record sterilization entry"""
        if not person_name or person_name.strip() == '':
            return False, "Person name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        if bag_quantity <= 0 and pcs_quantity <= 0:
            return False, "At least one quantity must be greater than 0"
        
        person_name = person_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        self.db.add_sterilization_entry(entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark)
        return True, f"✅ LOT {lot_number}: {bag_quantity} Bags / {pcs_quantity} Pcs entered for sterilization"
    
    def get_sterilization_entries(self):
        """Get all sterilization entries"""
        return self.db.get_sterilization_entries()
    
    def add_sterilization_start(self, start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        """Record sterilization start"""
        if not operator_name or operator_name.strip() == '':
            return False, "Operator name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        
        operator_name = operator_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        self.db.add_sterilization_start(start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        return True, f"✅ LOT {lot_number}: Sterilization started by {operator_name}"
    
    def add_sterilization_finish(self, finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        """Record sterilization finish"""
        if not operator_name or operator_name.strip() == '':
            return False, "Operator name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        
        operator_name = operator_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        self.db.add_sterilization_finish(finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        return True, f"✅ LOT {lot_number}: Sterilization finished by {operator_name}"
    
    def get_sterilization_starts(self):
        """Get all sterilization starts"""
        return self.db.get_sterilization_starts()
    
    def get_sterilization_finishes(self):
        """Get all sterilization finishes"""
        return self.db.get_sterilization_finishes()
    
    # ============================================
    # PRODUCTION - PACKING AFTER STERILIZATION
    # ============================================
    def add_packing_after_sterile(self, pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark=''):
        """Record packing after sterilization"""
        if not packer_name or packer_name.strip() == '':
            return False, "Packer name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        if bag_quantity <= 0 and pcs_quantity <= 0:
            return False, "At least one quantity must be greater than 0"
        
        packer_name = packer_name.strip().title()
        lot_number = lot_number.strip().upper()
        
        self.db.add_packing_after_sterile(pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark)
        return True, f"✅ LOT {lot_number}: {bag_quantity} Bags / {pcs_quantity} Pcs packed after sterilization"
    
    def get_packing_after_sterile(self):
        """Get all packing after sterile records"""
        return self.db.get_packing_after_sterile()
    
    # ============================================
    # HR - EMPLOYEE MANAGEMENT
    # ============================================
    def add_employee(self, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path):
        """Add a new employee"""
        if not full_name or full_name.strip() == '':
            return False, "Employee name cannot be empty"
        
        full_name = full_name.strip().title()
        
        employee_code = self.db.get_next_employee_code()
        
        self.db.add_employee(employee_code, full_name, national_id, mobile1, mobile2, address, blood_group, picture_path)
        return True, f"✅ Employee '{full_name}' added with code {employee_code}"
    
    def get_all_employees(self):
        """Get all employees"""
        return self.db.get_all_employees()
    
    def get_employee_names(self):
        """Get employee names for dropdown"""
        return self.db.get_employee_names()
    
    def delete_employee(self, employee_code):
        """Delete an employee"""
        if self.db.delete_employee(employee_code):
            return True, f"✅ Employee '{employee_code}' deleted!"
        return False, "❌ Failed to delete employee"
    
    # ============================================
    # HR - ATTENDANCE
    # ============================================
    def add_attendance(self, attendance_date, employee_code, check_in_time, status='Present', remark=''):
        """Record attendance"""
        if not employee_code or employee_code.strip() == '':
            return False, "Employee code cannot be empty"
        
        if self.db.add_attendance(attendance_date, employee_code, check_in_time, status, remark):
            return True, f"✅ Attendance recorded for {employee_code}"
        else:
            return False, f"❌ Attendance already recorded for {employee_code} on this date"
    
    def get_attendance(self, date=None):
        """Get attendance records"""
        return self.db.get_attendance(date)
    
    def get_today_attendance(self):
        """Get today's attendance"""
        return self.db.get_today_attendance()
    
    # ============================================
    # SYSTEM - LANGUAGE
    # ============================================
    def get_language(self):
        """Get current language setting"""
        return self.db.get_language()
    
    def set_language(self, language):
        """Set language setting"""
        return self.db.set_language(language)
    
    # ============================================
    # REPORTS
    # ============================================
    def get_daily_production_report(self):
        """Get daily production report"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        assembly = self.db.get_today_assembly()
        packing = self.db.get_packing_before_seal()
        sealing = self.db.get_sealing_records()
        sterilization_entries = self.db.get_sterilization_entries()
        
        today_packing = [p for p in packing if p[1] == today]
        today_sealing = [s for s in sealing if s[1] == today]
        today_sterilization = [s for s in sterilization_entries if s[1] == today]
        
        return {
            'date': today,
            'assembly_total': assembly,
            'packing_total': len(today_packing),
            'sealing_total': len(today_sealing),
            'sterilization_total': len(today_sterilization)
        }
    
    def get_sterilized_goods_report(self):
        """Get sterilized goods report"""
        return self.db.get_sterilized_goods_report()
    
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
        
        # Add order
        self.db.add_sales_order(order_number, customer_code, order_date, delivery_date, status, notes, created_by)
        
        # Add items and calculate total
        total_amount = 0
        for item in items:
            item_name = item.get('item_name')
            quantity = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total_price = quantity * unit_price
            total_amount += total_price
            self.db.add_sales_order_item(order_number, item_name, quantity, unit_price, total_price)
        
        # Update order total
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
        # Get order details
        order, items = self.db.get_order_by_number(order_number)
        if not order:
            return False, "Order not found"
        
        customer_code = order[2]
        total_amount = order[6]
        
        invoice_number = self.db.get_next_invoice_number()
        status = 'Unpaid'
        paid_amount = 0
        
        self.db.add_invoice(invoice_number, order_number, customer_code, invoice_date, due_date, total_amount, paid_amount, status, notes)
        
        # Update order status to Invoiced
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
    
    def delete_assembly_record(self, record_id):
        return self.db.delete_assembly_record(record_id)
    
    def delete_packing_before_seal(self, record_id):
        return self.db.delete_packing_before_seal(record_id)
    
    def delete_sealing_record(self, record_id):
        return self.db.delete_sealing_record(record_id)
    
    def delete_sterilization_entry(self, record_id):
        return self.db.delete_sterilization_entry(record_id)
    
    def delete_packing_after_sterile(self, record_id):
        return self.db.delete_packing_after_sterile(record_id)

    # ============================================
# SALES - DELETE METHODS
# ============================================
def delete_customer(self, customer_code):
    if self.db.delete_customer(customer_code):
        return True, f"✅ Customer '{customer_code}' deleted!"
    return False, "❌ Failed to delete customer"

def delete_order(self, order_number):
    if self.db.delete_order(order_number):
        return True, f"✅ Order '{order_number}' deleted!"
    return False, "❌ Failed to delete order"