from flask import Flask, render_template, request, redirect, url_for, session, flash
from business import ProductionManager
from auth_manager import AuthManager
from translations import get_tr
from datetime import datetime
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'change-this-to-something-random-later'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

manager = ProductionManager()
auth = AuthManager()

# ============================================
# LOW STOCK THRESHOLDS
# ============================================
def setup_thresholds_table():
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS low_stock_thresholds (
            item_name TEXT PRIMARY KEY,
            threshold INTEGER DEFAULT 10
        )
    """)
    conn.commit()
    conn.close()

def get_thresholds():
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, threshold FROM low_stock_thresholds")
    result = dict(cursor.fetchall())
    conn.close()
    return result

def set_threshold(item_name, threshold):
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO low_stock_thresholds (item_name, threshold) VALUES (?, ?) "
        "ON CONFLICT(item_name) DO UPDATE SET threshold = excluded.threshold",
        (item_name, threshold)
    )
    conn.commit()
    conn.close()

setup_thresholds_table()

# ============================================
# APP SETTINGS
# ============================================
DEFAULT_SETTINGS = {
    'font_size': '14',
    'font_family': 'Segoe UI',
    'default_language': 'EN',
    'background_image': '',
    'background_opacity': '100',
    'fit_to_window': 'off',
    'tab_view': 'sidebar',
    'backup_folder': 'static/uploads',
    'theme': 'industrial'
}

def setup_settings_table():
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_settings():
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM app_settings")
    stored = dict(cursor.fetchall())
    conn.close()
    result = dict(DEFAULT_SETTINGS)
    result.update(stored)
    return result

def set_setting(key, value):
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO app_settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value)
    )
    conn.commit()
    conn.close()

setup_settings_table()

# ============================================
# CONTEXT PROCESSOR
# ============================================
@app.context_processor
def inject_settings():
    settings = get_all_settings()
    lang = session.get('lang', settings.get('default_language', 'EN'))
    return {
        'app_settings': settings,
        'tr': get_tr(lang),
        'current_lang': lang
    }

def login_required():
    return 'user' not in session

# ============================================
# AUTH ROUTES
# ============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        success, message = auth.login(username, password)
        if success:
            session['user'] = auth.get_current_user()
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=message, login_lang=session.get('login_lang', 'EN'))
    return render_template('login.html', error=None, login_lang=session.get('login_lang', 'EN'))

@app.route('/toggle_login_lang', methods=['POST'])
def toggle_login_lang():
    current = session.get('login_lang', 'EN')
    if current == 'EN':
        session['login_lang'] = 'RU'
    elif current == 'RU':
        session['login_lang'] = 'BOTH'
    else:
        session['login_lang'] = 'EN'
    return redirect(url_for('login'))

@app.route('/set_language', methods=['POST'])
def set_language():
    current = session.get('lang', 'EN')
    if current == 'EN':
        session['lang'] = 'RU'
    elif current == 'RU':
        session['lang'] = 'BOTH'
    else:
        session['lang'] = 'EN'
    return redirect(request.referrer or url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ============================================
# DASHBOARD
# ============================================
@app.route('/')
def home():
    if login_required():
        return redirect(url_for('login'))

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantity) FROM assembly_records WHERE assembly_date = ?", (today,))
    today_total = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT assembly_date, 'Assembly', assembler_name, quantity FROM assembly_records ORDER BY timestamp DESC LIMIT 5"
    )
    recent = cursor.fetchall()

    cursor.execute("SELECT SUM(quantity) FROM checking_records")
    total_checking = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(quantity) FROM assembly_records")
    total_assembly = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(quantity) FROM packing_before_seal")
    total_packing = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(sealing_qty) FROM sealing_records")
    total_sealing = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(pcs_quantity) FROM sterilization_finish")
    total_sterilized = cursor.fetchone()[0] or 0
    conn.close()

    total_employees = len(manager.get_all_employees())
    stock = manager.get_warehouse_stock()
    raw_materials = manager.get_raw_material_entries()
    all_products = manager.get_all_products()

    stock_by_item = {}
    for p in all_products:
        stock_by_item[p[0]] = {'entries': [], 'total': 0, 'unit': p[1]}

    for r in raw_materials:
        item_name = r[5]
        invoice_number = r[4]
        quantity = r[6]
        unit = r[7]
        if item_name not in stock_by_item:
            stock_by_item[item_name] = {'entries': [], 'total': 0, 'unit': unit}
        stock_by_item[item_name]['entries'].append((invoice_number, quantity))
        stock_by_item[item_name]['total'] += quantity

    thresholds = get_thresholds()
    for item_name in stock_by_item:
        stock_by_item[item_name]['threshold'] = thresholds.get(item_name, 10)
        stock_by_item[item_name]['low_stock'] = stock_by_item[item_name]['total'] <= stock_by_item[item_name]['threshold']

    return render_template(
        'dashboard.html',
        active='dashboard',
        today_total=today_total,
        total_employees=total_employees,
        stock=stock,
        stock_by_item=stock_by_item,
        recent=recent,
        total_checking=total_checking,
        total_assembly=total_assembly,
        total_packing=total_packing,
        total_sealing=total_sealing,
        total_sterilized=total_sterilized
    )

# ============================================
# WAREHOUSE ROUTES (FULL CRUD)
# ============================================
@app.route('/warehouse')
def warehouse():
    if login_required():
        return redirect(url_for('login'))

    products = manager.get_all_products()
    stock = manager.get_warehouse_stock()
    suppliers = manager.get_all_suppliers()
    raw_materials = manager.get_raw_material_entries()

    return render_template(
        'warehouse.html',
        active='warehouse',
        products=products,
        stock_items=stock['items'],
        suppliers=suppliers,
        raw_materials=raw_materials
    )

# Products - CRUD
@app.route('/warehouse/add_product', methods=['POST'])
def add_product():
    if login_required():
        return redirect(url_for('login'))
    product_name = request.form.get('product_name', '')
    unit = request.form.get('unit', 'PCS')
    low_stock_qty = int(request.form.get('low_stock_qty', 10))
    manager.add_product(product_name, unit)
    set_threshold(product_name, low_stock_qty)
    flash(f'✅ Product "{product_name}" added successfully!', 'success')
    return redirect(url_for('warehouse'))

@app.route('/warehouse/delete_product/<product_name>', methods=['POST'])
def delete_product(product_name):
    if login_required():
        return redirect(url_for('login'))
    success, message = manager.delete_product(product_name)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('warehouse'))

# Suppliers - CRUD
@app.route('/warehouse/add_supplier', methods=['POST'])
def add_supplier():
    if login_required():
        return redirect(url_for('login'))
    supplier_name = request.form.get('supplier_name', '')
    supplier_address = request.form.get('supplier_address', '')
    contact_person = request.form.get('contact_person', '')
    phone = request.form.get('phone', '')
    success, message = manager.add_supplier(supplier_name, supplier_address, contact_person, phone)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('warehouse'))

@app.route('/warehouse/delete_supplier/<supplier_name>', methods=['POST'])
def delete_supplier(supplier_name):
    if login_required():
        return redirect(url_for('login'))
    success, message = manager.delete_supplier(supplier_name)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('warehouse'))

# Raw Material - CRUD
@app.route('/warehouse/add_raw_material', methods=['POST'])
def add_raw_material():
    if login_required():
        return redirect(url_for('login'))
    supplier_name = request.form.get('supplier_name', '')
    invoice_number = request.form.get('invoice_number', '')
    item_name = request.form.get('item_name', '')
    quantity = int(request.form.get('quantity', 0))
    unit = request.form.get('unit', 'PCS')
    received_by = request.form.get('received_by', '')
    entry_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_raw_material_entry(
        supplier_name, '', entry_date, invoice_number,
        item_name, quantity, unit, received_by
    )
    flash(message, 'success' if success else 'error')
    return redirect(url_for('warehouse'))

@app.route('/warehouse/delete_raw_material/<int:record_id>', methods=['POST'])
def delete_raw_material(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_raw_material_entry(record_id)
    flash('✅ Record deleted!', 'success')
    return redirect(url_for('warehouse'))

# Update Stock Threshold
@app.route('/warehouse/update_threshold', methods=['POST'])
def update_threshold():
    if login_required():
        return redirect(url_for('login'))
    item_name = request.form.get('item_name', '')
    threshold = int(request.form.get('threshold', 10))
    set_threshold(item_name, threshold)
    flash(f'✅ Threshold for "{item_name}" updated to {threshold}!', 'success')
    return redirect(url_for('warehouse'))

# ============================================
# PRODUCTION ROUTES (FULL CRUD)
# ============================================
@app.route('/production')
def production():
    if login_required():
        return redirect(url_for('login'))

    products = manager.get_all_products()
    transfers = manager.get_transfers_to_production()
    checking_records = manager.get_checking_records()
    assembly_records = manager.get_assembly_records()
    packing_records = manager.get_packing_before_seal()
    sealing_records = manager.get_sealing_records()
    sterilization_entries = manager.get_sterilization_entries()
    sterilization_starts = manager.get_sterilization_starts()
    sterilization_finishes = manager.get_sterilization_finishes()
    packing_after_sterile = manager.get_packing_after_sterile()

    return render_template(
        'production.html',
        active='production',
        products=products,
        transfers=transfers,
        checking_records=checking_records,
        assembly_records=assembly_records,
        packing_records=packing_records,
        sealing_records=sealing_records,
        sterilization_entries=sterilization_entries,
        sterilization_starts=sterilization_starts,
        sterilization_finishes=sterilization_finishes,
        packing_after_sterile=packing_after_sterile
    )

# Transfer - CRUD
@app.route('/production/transfer', methods=['POST'])
def production_transfer():
    if login_required():
        return redirect(url_for('login'))
    item_name = request.form.get('item_name', '')
    quantity = int(request.form.get('quantity', 0))
    unit = request.form.get('unit', 'PCS')
    received_by = request.form.get('received_by', '')
    issued_by = request.form.get('issued_by', '')
    transfer_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.transfer_to_production(item_name, quantity, unit, received_by, issued_by, transfer_date)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_transfer/<int:record_id>', methods=['POST'])
def delete_transfer(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_transfer_to_production(record_id)
    flash('✅ Transfer record deleted!', 'success')
    return redirect(url_for('production'))

# Checking - CRUD
@app.route('/production/checking', methods=['POST'])
def production_checking():
    if login_required():
        return redirect(url_for('login'))
    item_name = request.form.get('item_name', '')
    quantity = int(request.form.get('quantity', 0))
    unit = request.form.get('unit', 'PCS')
    checker_name = request.form.get('checker_name', '')
    check_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_checking_record(check_date, item_name, quantity, unit, checker_name)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_checking/<int:record_id>', methods=['POST'])
def delete_checking(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_checking_record(record_id)
    flash('✅ Checking record deleted!', 'success')
    return redirect(url_for('production'))

# Assembly - CRUD
@app.route('/production/assembly', methods=['POST'])
def production_assembly():
    if login_required():
        return redirect(url_for('login'))
    quantity = int(request.form.get('quantity', 0))
    unit = request.form.get('unit', 'PCS')
    assembler_name = request.form.get('assembler_name', '')
    assembly_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_assembly_record(assembly_date, assembler_name, quantity, unit)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_assembly/<int:record_id>', methods=['POST'])
def delete_assembly(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_assembly_record(record_id)
    flash('✅ Assembly record deleted!', 'success')
    return redirect(url_for('production'))

# Packing Before Seal - CRUD
@app.route('/production/packing_before_seal', methods=['POST'])
def production_packing_before_seal():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    quantity = int(request.form.get('quantity', 0))
    unit = request.form.get('unit', 'PCS')
    packer_name = request.form.get('packer_name', '')
    pack_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_packing_before_seal(pack_date, packer_name, lot_number, quantity, unit)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_packing/<int:record_id>', methods=['POST'])
def delete_packing(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_packing_before_seal(record_id)
    flash('✅ Packing record deleted!', 'success')
    return redirect(url_for('production'))

# Sealing - CRUD
@app.route('/production/sealing', methods=['POST'])
def production_sealing():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    sealing_qty = int(request.form.get('sealing_qty', 0))
    packing_qty = int(request.form.get('packing_qty', 0))
    sealer_name = request.form.get('sealer_name', '')
    seal_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_sealing_record(seal_date, sealer_name, lot_number, sealing_qty, packing_qty)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_sealing/<int:record_id>', methods=['POST'])
def delete_sealing(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_sealing_record(record_id)
    flash('✅ Sealing record deleted!', 'success')
    return redirect(url_for('production'))

# Sterilization Entry - CRUD
@app.route('/production/sterilization_entry', methods=['POST'])
def sterilization_entry():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    bag_quantity = int(request.form.get('bag_quantity', 0))
    pcs_quantity = int(request.form.get('pcs_quantity', 0))
    person_name = request.form.get('person_name', '')
    entry_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_sterilization_entry(entry_date, person_name, bag_quantity, pcs_quantity, lot_number)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_sterilization_entry/<int:record_id>', methods=['POST'])
def delete_sterilization_entry(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_sterilization_entry(record_id)
    flash('✅ Sterilization entry deleted!', 'success')
    return redirect(url_for('production'))

# Sterilization Start
@app.route('/production/sterilization_start', methods=['POST'])
def sterilization_start():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    bag_quantity = int(request.form.get('bag_quantity', 0))
    pcs_quantity = int(request.form.get('pcs_quantity', 0))
    operator_name = request.form.get('operator_name', '')
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success, message = manager.add_sterilization_start(start_datetime, operator_name, bag_quantity, pcs_quantity, lot_number)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

# Sterilization Finish
@app.route('/production/sterilization_finish', methods=['POST'])
def sterilization_finish():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    bag_quantity = int(request.form.get('bag_quantity', 0))
    pcs_quantity = int(request.form.get('pcs_quantity', 0))
    operator_name = request.form.get('operator_name', '')
    finish_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success, message = manager.add_sterilization_finish(finish_datetime, operator_name, bag_quantity, pcs_quantity, lot_number)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

# Packing After Sterile - CRUD
@app.route('/production/packing_after_sterile', methods=['POST'])
def packing_after_sterile():
    if login_required():
        return redirect(url_for('login'))
    lot_number = request.form.get('lot_number', '')
    bag_quantity = int(request.form.get('bag_quantity', 0))
    pcs_quantity = int(request.form.get('pcs_quantity', 0))
    packer_name = request.form.get('packer_name', '')
    pack_date = datetime.now().strftime("%Y-%m-%d")
    success, message = manager.add_packing_after_sterile(pack_date, packer_name, lot_number, bag_quantity, pcs_quantity)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('production'))

@app.route('/production/delete_pack_after/<int:record_id>', methods=['POST'])
def delete_pack_after(record_id):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_packing_after_sterile(record_id)
    flash('✅ Packing after sterile record deleted!', 'success')
    return redirect(url_for('production'))

# ============================================
# HR ROUTES
# ============================================
@app.route('/hr')
def hr():
    if login_required():
        return redirect(url_for('login'))
    employees = manager.get_all_employees()
    today = datetime.now().strftime("%Y-%m-%d")
    attendance = manager.get_attendance(today)
    return render_template('hr.html', active='hr', employees=employees, attendance=attendance)

@app.route('/hr/add_employee', methods=['POST'])
def add_employee():
    if login_required():
        return redirect(url_for('login'))
    full_name = request.form.get('full_name', '')
    national_id = request.form.get('national_id', '')
    mobile1 = request.form.get('mobile1', '')
    mobile2 = request.form.get('mobile2', '')
    address = request.form.get('address', '')
    blood_group = request.form.get('blood_group', '')
    success, message = manager.add_employee(full_name, national_id, mobile1, mobile2, address, blood_group, '')
    flash(message, 'success' if success else 'error')
    return redirect(url_for('hr'))

@app.route('/hr/delete_employee/<employee_code>', methods=['POST'])
def delete_employee(employee_code):
    if login_required():
        return redirect(url_for('login'))
    success, message = manager.delete_employee(employee_code)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('hr'))

@app.route('/hr/mark_attendance', methods=['POST'])
def mark_attendance():
    if login_required():
        return redirect(url_for('login'))
    employee_code = request.form.get('employee_code', '')
    status = request.form.get('status', 'Present')
    today = datetime.now().strftime("%Y-%m-%d")
    check_in_time = datetime.now().strftime("%H:%M:%S")
    success, message = manager.add_attendance(today, employee_code, check_in_time, status)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('hr'))

@app.route('/hr/attendance_by_date', methods=['GET'])
def attendance_by_date():
    if login_required():
        return redirect(url_for('login'))
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    employees = manager.get_all_employees()
    attendance = manager.get_attendance(date)
    return render_template('hr.html', active='hr', employees=employees, attendance=attendance, selected_date=date)

# ============================================
# SALES ROUTES (FULL CRUD)
# ============================================
@app.route('/sales')
def sales():
    if login_required():
        return redirect(url_for('login'))
    
    customers = manager.get_all_customers()
    orders = manager.get_all_orders()
    invoices = manager.get_all_invoices()
    products = manager.get_all_products()
    now = datetime.now().strftime("%Y-%m-%d")
    
    return render_template(
        'sales.html',
        active='sales',
        customers=customers,
        orders=orders,
        invoices=invoices,
        products=products,
        now=now
    )

# Customers - CRUD
@app.route('/sales/add_customer', methods=['POST'])
def add_customer():
    if login_required():
        return redirect(url_for('login'))
    customer_name = request.form.get('customer_name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    city = request.form.get('city', '')
    country = request.form.get('country', '')
    success, message = manager.add_customer(customer_name, email, phone, address, city, country)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('sales'))

@app.route('/sales/delete_customer/<customer_code>', methods=['POST'])
def delete_customer(customer_code):
    if login_required():
        return redirect(url_for('login'))
    success, message = manager.delete_customer(customer_code)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('sales'))

# Orders - CRUD
@app.route('/sales/create_order', methods=['POST'])
def create_order():
    if login_required():
        return redirect(url_for('login'))
    customer_code = request.form.get('customer_code', '')
    order_date = request.form.get('order_date', '')
    delivery_date = request.form.get('delivery_date', '')
    notes = request.form.get('notes', '')
    created_by = session['user']['full_name']
    
    items = []
    item_names = request.form.getlist('item_name[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('unit_price[]')
    
    for i in range(len(item_names)):
        if item_names[i] and int(quantities[i]) > 0:
            items.append({
                'item_name': item_names[i],
                'quantity': int(quantities[i]),
                'unit_price': float(prices[i])
            })
    
    success, message = manager.create_sales_order(customer_code, order_date, delivery_date, items, notes, created_by)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('sales'))

@app.route('/sales/update_status', methods=['POST'])
def update_order_status():
    if login_required():
        return redirect(url_for('login'))
    order_number = request.form.get('order_number', '')
    status = request.form.get('status', '')
    manager.update_order_status(order_number, status)
    flash('✅ Order status updated!', 'success')
    return redirect(url_for('sales'))

@app.route('/sales/delete_order/<order_number>', methods=['POST'])
def delete_order(order_number):
    if login_required():
        return redirect(url_for('login'))
    manager.delete_order(order_number)
    flash('✅ Order deleted!', 'success')
    return redirect(url_for('sales'))

# Invoices - CRUD
@app.route('/sales/create_invoice', methods=['POST'])
def create_invoice():
    if login_required():
        return redirect(url_for('login'))
    order_number = request.form.get('order_number', '')
    invoice_date = request.form.get('invoice_date', datetime.now().strftime("%Y-%m-%d"))
    due_date = request.form.get('due_date', '')
    notes = request.form.get('notes', '')
    success, message = manager.create_invoice(order_number, invoice_date, due_date, notes)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('sales'))

@app.route('/sales/record_payment', methods=['POST'])
def record_payment():
    if login_required():
        return redirect(url_for('login'))
    invoice_number = request.form.get('invoice_number', '')
    amount = float(request.form.get('amount', 0))
    if amount <= 0:
        flash('❌ Payment amount must be greater than 0!', 'error')
        return redirect(url_for('sales'))
    manager.record_payment(invoice_number, amount)
    flash('✅ Payment recorded successfully!', 'success')
    return redirect(url_for('sales'))

@app.route('/sales/delete_invoice/<invoice_number>', methods=['POST'])
def delete_invoice(invoice_number):
    if login_required():
        return redirect(url_for('login'))
    # Add delete method to database
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
    conn.commit()
    conn.close()
    flash('✅ Invoice deleted!', 'success')
    return redirect(url_for('sales'))

# ============================================
# REPORTS ROUTES
# ============================================
@app.route('/reports')
def reports():
    if login_required():
        return redirect(url_for('login'))

    selected_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))

    today_assembly = manager.get_today_assembly()
    stock = manager.get_warehouse_stock()
    sterilized = manager.get_sterilized_goods_report()
    total_employees = len(manager.get_all_employees())
    sterilization_entries = manager.get_sterilization_entries()
    attendance = manager.get_attendance(selected_date)

    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 'Assembly', assembler_name, quantity, assembly_date, '' FROM assembly_records ORDER BY timestamp DESC LIMIT 10"
    )
    production_report = cursor.fetchall()
    cursor.execute(
        "SELECT 'Packing', packer_name, quantity, pack_date, lot_number FROM packing_before_seal ORDER BY timestamp DESC LIMIT 10"
    )
    production_report += cursor.fetchall()
    cursor.execute(
        "SELECT 'Sealing', sealer_name, sealing_qty, seal_date, lot_number FROM sealing_records ORDER BY timestamp DESC LIMIT 10"
    )
    production_report += cursor.fetchall()
    conn.close()

    return render_template(
        'reports.html',
        active='reports',
        today_assembly=today_assembly,
        stock=stock,
        sterilized=sterilized,
        total_employees=total_employees,
        sterilization_entries=sterilization_entries,
        attendance=attendance,
        production_report=production_report,
        selected_date=selected_date
    )

# ============================================
# SETTINGS ROUTES
# ============================================
@app.route('/settings')
def settings():
    if login_required():
        return redirect(url_for('login'))
    return render_template('settings.html', active='settings')

@app.route('/settings/apply', methods=['POST'])
def settings_apply():
    if login_required():
        return redirect(url_for('login'))

    set_setting('font_size', request.form.get('font_size', '14'))
    set_setting('font_family', request.form.get('font_family', 'Segoe UI'))
    set_setting('default_language', request.form.get('default_language', 'EN'))
    set_setting('background_opacity', request.form.get('background_opacity', '100'))
    set_setting('fit_to_window', 'on' if request.form.get('fit_to_window') else 'off')
    set_setting('tab_view', request.form.get('tab_view', 'sidebar'))
    set_setting('theme', request.form.get('theme', 'industrial'))

    bg_file = request.files.get('background_image')
    if bg_file and bg_file.filename:
        filename = secure_filename(bg_file.filename)
        bg_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        set_setting('background_image', filename)

    flash('✅ Settings applied!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/remove_background', methods=['POST'])
def settings_remove_background():
    if login_required():
        return redirect(url_for('login'))
    set_setting('background_image', '')
    flash('✅ Background image removed!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/set_backup_folder', methods=['POST'])
def settings_set_backup_folder():
    if login_required():
        return redirect(url_for('login'))
    set_setting('backup_folder', request.form.get('backup_folder', 'static/uploads'))
    flash('✅ Backup folder saved!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/reset_appearance', methods=['POST'])
def settings_reset_appearance():
    if login_required():
        return redirect(url_for('login'))
    for key, value in DEFAULT_SETTINGS.items():
        set_setting(key, value)
    flash('✅ Appearance reset to default!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/backup', methods=['POST'])
def settings_backup():
    if login_required():
        return redirect(url_for('login'))
    import shutil
    settings_now = get_all_settings()
    backup_folder = settings_now.get('backup_folder', 'static/uploads')
    os.makedirs(backup_folder, exist_ok=True)
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(backup_folder, backup_name)
    shutil.copy2('production.db', backup_path)
    flash(f'✅ Backup created: {backup_path}', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/restore', methods=['POST'])
def settings_restore():
    if login_required():
        return redirect(url_for('login'))
    restore_file = request.files.get('restore_file')
    if not restore_file or not restore_file.filename.endswith('.db'):
        flash('❌ Please choose a valid .db backup file!', 'error')
        return redirect(url_for('settings'))
    import shutil
    shutil.copy2('production.db', 'production_before_restore.db')
    restore_file.save('production.db')
    flash('✅ Database restored! Please restart the app.', 'success')
    return redirect(url_for('settings'))

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    app.run(debug=True)