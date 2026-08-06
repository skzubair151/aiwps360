# PART 2: BUSINESS LOGIC LAYER (COMPLETE - WITH SALES + IV SET)
from database import Database
from datetime import datetime, timedelta

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
    # WAREHOUSE - RAW MATERIAL ENTRY
    # ============================================
    def add_raw_material_entry(self, supplier_name, supplier_address, entry_date, invoice_number, item_name, quantity, unit, received_by):
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
    # PRODUCTION - WAREHOUSE TO PRODUCTION
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
        available, unit_db = self.db.get_item_quantity(item_name)
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
    
    def get_today_assembly(self):
        return self.db.get_today_assembly()
    
    # ============================================
    # PRODUCTION - PACKING BEFORE SEAL
    # ============================================
    def add_packing_before_seal(self, pack_date, packer_name, lot_number, quantity, unit):
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
        return self.db.get_packing_before_seal()
    
    def get_all_lot_numbers(self):
        return self.db.get_all_lot_numbers()
    
    def get_lot_info(self, lot_number):
        return self.db.get_lot_info(lot_number)
    
    # ============================================
    # PRODUCTION - SEALING
    # ============================================
    def add_sealing_record(self, seal_date, sealer_name, lot_number, sealing_qty, packing_qty):
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
        return self.db.get_sealing_records()
    
    # ============================================
    # PRODUCTION - STERILIZATION
    # ============================================
    def add_sterilization_entry(self, entry_date, person_name, bag_quantity, pcs_quantity, lot_number, remark=''):
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
        return self.db.get_sterilization_entries()
    
    def add_sterilization_start(self, start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        if not operator_name or operator_name.strip() == '':
            return False, "Operator name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        operator_name = operator_name.strip().title()
        lot_number = lot_number.strip().upper()
        self.db.add_sterilization_start(start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        return True, f"✅ LOT {lot_number}: Sterilization started by {operator_name}"
    
    def add_sterilization_finish(self, finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark=''):
        if not operator_name or operator_name.strip() == '':
            return False, "Operator name cannot be empty"
        if not lot_number or lot_number.strip() == '':
            return False, "Lot number cannot be empty"
        operator_name = operator_name.strip().title()
        lot_number = lot_number.strip().upper()
        self.db.add_sterilization_finish(finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number, remark)
        return True, f"✅ LOT {lot_number}: Sterilization finished by {operator_name}"
    
    def get_sterilization_starts(self):
        return self.db.get_sterilization_starts()
    
    def get_sterilization_finishes(self):
        return self.db.get_sterilization_finishes()
    
    # ============================================
    # PRODUCTION - PACKING AFTER STERILE
    # ============================================
    def add_packing_after_sterile(self, pack_date, packer_name, lot_number, bag_quantity, pcs_quantity, remark=''):
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
        return self.db.get_packing_after_sterile()
    
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
    # REPORTS
    # ============================================
    def get_daily_production_report(self):
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
    # IV SET - ASSEMBLY
    # ============================================
    def get_iv_set_bom(self):
        return self.db.get_iv_set_bom()

    def check_iv_set_stock(self, quantity):
        return self.db.check_iv_set_stock(quantity)

    def assemble_iv_sets(self, quantity, assembler_name):
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        if not assembler_name or assembler_name.strip() == '':
            return False, "Assembler name cannot be empty"
        
        can_assemble, components, shortages = self.db.check_iv_set_stock(quantity)
        if not can_assemble:
            return False, f"❌ Not enough components! Shortages: {', '.join(shortages)}"
        
        self.db.deduct_iv_set_components(quantity)
        batch_number = self.db.get_next_batch_number()
        assembly_date = datetime.now().strftime("%Y-%m-%d")
        
        self.db.add_iv_set_assembly(
            assembly_date, batch_number, quantity,
            quantity, quantity, quantity, quantity, quantity,
            assembler_name
        )
        return True, f"✅ Batch {batch_number}: {quantity} IV Sets assembled by {assembler_name}"

    def get_iv_set_assembly_records(self):
        return self.db.get_iv_set_assembly_records()

    # ============================================
    # IV SET - PACKING (Single Pack)
    # ============================================
    def pack_iv_sets(self, batch_number, packer_name):
        if not batch_number:
            return False, "Batch number cannot be empty"
        if not packer_name or packer_name.strip() == '':
            return False, "Packer name cannot be empty"
        
        records = self.db.get_iv_set_assembly_records()
        batch = None
        for r in records:
            if r[2] == batch_number:
                batch = r
                break
        
        if not batch:
            return False, f"❌ Batch {batch_number} not found!"
        if batch[5] != 'Pending':
            return False, f"❌ Batch {batch_number} already packed!"
        
        total_sets = batch[3]
        available, unit = self.db.get_item_quantity('Single Pack Poly')
        if available < total_sets:
            return False, f"❌ Not enough Single Pack Poly! Available: {available}, Required: {total_sets}"
        
        lot_number = f"LOT{datetime.now().strftime('%Y%m%d')}-{batch_number}"
        pack_date = datetime.now().strftime("%Y-%m-%d")
        
        self.db.add_iv_set_packing(pack_date, batch_number, total_sets, total_sets, packer_name, lot_number)
        self.db.update_assembly_status(batch_number, 'Packed')
        return True, f"✅ LOT {lot_number}: {total_sets} IV Sets packed by {packer_name}"

    def get_iv_set_packing_records(self):
        return self.db.get_iv_set_packing_records()

    def get_pending_batches_for_packing(self):
        return self.db.get_pending_batches_for_packing()

    # ============================================
    # IV SET - SEALING (Multi Pack)
    # ============================================
    def seal_iv_sets(self, lot_number, sets_per_pack, sealer_name):
        if not lot_number:
            return False, "LOT number cannot be empty"
        if sets_per_pack <= 0:
            return False, "Sets per pack must be greater than 0"
        if not sealer_name or sealer_name.strip() == '':
            return False, "Sealer name cannot be empty"
        
        records = self.db.get_iv_set_packing_records()
        pack_record = None
        for r in records:
            if r[5] == lot_number:
                pack_record = r
                break
        
        if not pack_record:
            return False, f"❌ LOT {lot_number} not found!"
        
        total_sets = pack_record[3]
        multi_pack_qty = (total_sets + sets_per_pack - 1) // sets_per_pack
        
        available, unit = self.db.get_item_quantity('Multi Pack Poly')
        if available < multi_pack_qty:
            return False, f"❌ Not enough Multi Pack Poly! Available: {available}, Required: {multi_pack_qty}"
        
        seal_date = datetime.now().strftime("%Y-%m-%d")
        self.db.add_iv_set_sealing(seal_date, lot_number, multi_pack_qty, sets_per_pack, total_sets, sealer_name)
        self.db.update_packing_status(lot_number, 'Sealed')
        return True, f"✅ {multi_pack_qty} Multi Packs created from LOT {lot_number} ({total_sets} IV Sets)"

    def get_iv_set_sealing_records(self):
        return self.db.get_iv_set_sealing_records()

    def get_pending_lots_for_sealing(self):
        return self.db.get_pending_lots_for_sealing()

    def delete_iv_set_assembly(self, record_id):
        return self.db.delete_iv_set_assembly(record_id)

    def delete_iv_set_packing(self, record_id):
        return self.db.delete_iv_set_packing(record_id)

    def delete_iv_set_sealing(self, record_id):
        return self.db.delete_iv_set_sealing(record_id)
    
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
# IV SET - TUBE INVENTORY (Bags/Cartons)
# ============================================
def add_tube_inventory(self, supplier_name, invoice_number, bag_quantity, pcs_per_bag, carton_quantity, pcs_per_carton, received_by):
    """Add tube inventory with bag and carton tracking"""
    total_pcs = (bag_quantity * pcs_per_bag) + (carton_quantity * pcs_per_carton)
    entry_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tube_inventory (entry_date, supplier_name, invoice_number, bag_quantity, pcs_per_bag, total_pcs, carton_quantity, pcs_per_carton, received_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (entry_date, supplier_name, invoice_number, bag_quantity, pcs_per_bag, total_pcs, carton_quantity, pcs_per_carton, received_by)
    )
    # Update warehouse stock for Tub
    cursor.execute(
        "UPDATE warehouse_stock SET quantity = quantity + ? WHERE item_name = 'Tub'",
        (total_pcs,)
    )
    conn.commit()
    conn.close()
    return True, f"✅ {bag_quantity} Bags ({bag_quantity * pcs_per_bag} PCS) + {carton_quantity} Cartons ({carton_quantity * pcs_per_carton} PCS) of Tube added"

def get_tube_inventory(self):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, entry_date, supplier_name, invoice_number, bag_quantity, pcs_per_bag, total_pcs, carton_quantity, pcs_per_carton, received_by FROM tube_inventory ORDER BY timestamp DESC")
    results = cursor.fetchall()
    conn.close()
    return results

# ============================================
# IV SET - ASSEMBLY (Updated with stock check)
# ============================================
def assemble_iv_sets(self, quantity, assembler_name):
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    if not assembler_name or assembler_name.strip() == '':
        return False, "Assembler name cannot be empty"
    
    # Check stock for all components
    components = ['Chamber', 'Needle 35mm', 'Roller', 'Latex', 'Tub']
    shortages = []
    stock_data = {}
    
    for comp in components:
        available, unit = self.db.get_item_quantity(comp)
        stock_data[comp] = available
        if available < quantity:
            shortages.append(f"{comp}: {available} available, {quantity} required")
    
    if shortages:
        return False, f"❌ Not enough components! Shortages: {', '.join(shortages)}"
    
    # Deduct all components
    for comp in components:
        self.db.deduct_warehouse_stock(comp, quantity)
    
    # Create batch
    batch_number = self.db.get_next_batch_number()
    assembly_date = datetime.now().strftime("%Y-%m-%d")
    
    self.db.add_iv_set_assembly(
        assembly_date, batch_number, quantity,
        quantity, quantity, quantity, quantity, quantity,
        assembler_name
    )
    return True, f"✅ Batch {batch_number}: {quantity} IV Sets assembled by {assembler_name}"

# ============================================
# IV SET - PACKING (Updated with stock check)
# ============================================
def pack_iv_sets(self, batch_number, packer_name):
    if not batch_number:
        return False, "Batch number cannot be empty"
    if not packer_name or packer_name.strip() == '':
        return False, "Packer name cannot be empty"
    
    records = self.db.get_iv_set_assembly_records()
    batch = None
    for r in records:
        if r[2] == batch_number:
            batch = r
            break
    
    if not batch:
        return False, f"❌ Batch {batch_number} not found!"
    if batch[5] != 'Pending':
        return False, f"❌ Batch {batch_number} already packed!"
    
    total_sets = batch[3]
    
    # Check Single Pack Poly stock
    available, unit = self.db.get_item_quantity('Single Pack Poly')
    if available < total_sets:
        return False, f"❌ Not enough Single Pack Poly! Available: {available}, Required: {total_sets}"
    
    # Deduct Single Pack Poly
    self.db.deduct_warehouse_stock('Single Pack Poly', total_sets)
    
    lot_number = f"LOT{datetime.now().strftime('%Y%m%d')}-{batch_number}"
    pack_date = datetime.now().strftime("%Y-%m-%d")
    
    self.db.add_iv_set_packing(pack_date, batch_number, total_sets, total_sets, packer_name, lot_number)
    self.db.update_assembly_status(batch_number, 'Packed')
    return True, f"✅ LOT {lot_number}: {total_sets} IV Sets packed by {packer_name}"

# ============================================
# IV SET - SEALING (Updated with stock check)
# ============================================
def seal_iv_sets(self, lot_number, sets_per_pack, sealer_name):
    if not lot_number:
        return False, "LOT number cannot be empty"
    if sets_per_pack <= 0:
        return False, "Sets per pack must be greater than 0"
    if not sealer_name or sealer_name.strip() == '':
        return False, "Sealer name cannot be empty"
    
    records = self.db.get_iv_set_packing_records()
    pack_record = None
    for r in records:
        if r[5] == lot_number:
            pack_record = r
            break
    
    if not pack_record:
        return False, f"❌ LOT {lot_number} not found!"
    
    total_sets = pack_record[3]
    multi_pack_qty = (total_sets + sets_per_pack - 1) // sets_per_pack
    
    # Check Multi Pack Poly stock
    available, unit = self.db.get_item_quantity('Multi Pack Poly')
    if available < multi_pack_qty:
        return False, f"❌ Not enough Multi Pack Poly! Available: {available}, Required: {multi_pack_qty}"
    
    # Deduct Multi Pack Poly
    self.db.deduct_warehouse_stock('Multi Pack Poly', multi_pack_qty)
    
    seal_date = datetime.now().strftime("%Y-%m-%d")
    self.db.add_iv_set_sealing(seal_date, lot_number, multi_pack_qty, sets_per_pack, total_sets, sealer_name)
    self.db.update_packing_status(lot_number, 'Sealed')
    return True, f"✅ {multi_pack_qty} Multi Packs created from LOT {lot_number} ({total_sets} IV Sets)"
