from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import mysql.connector
from dotenv import load_dotenv
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'ecommerce_website',
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied. Check your username and password.")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Error: Database 'ecommerce_website' does not exist.")
        else:
            print(f"Error: {err}")
        raise

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') == 'customer':
        return redirect(url_for('products'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Get password as-is
        user_type = request.form['user_type']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if user_type == 'customer':
                # For customers, check email and plain text password
                cursor.execute('SELECT * FROM Customer WHERE Customer_email = %s AND Customer_password = %s',
                             (email, password))
            else:
                # For employees, check email and plain text password
                cursor.execute('SELECT * FROM Employee WHERE Employee_email = %s AND Employee_password = %s',
                             (email, password))
            
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['Customer_id' if user_type == 'customer' else 'Employee_id']
                session['user_type'] = user_type
                session['user_name'] = user['Customer_name' if user_type == 'customer' else 'Employee_name']
                if user_type == 'customer':
                    return redirect(url_for('products'))
                else:
                    return redirect(url_for('admin_dashboard'))
            else:
                return render_template('login.html', error='Invalid email or password')
                
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return render_template('login.html', error='An error occurred during login')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']  # Store password as-is
            confirm_password = request.form['confirm_password']
            contact = request.form['contact']
            
            if password != confirm_password:
                return render_template('register.html', error='Passwords do not match')
            
            print(f"Attempting to register user: {name}, {email}")  # Debug log
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT Customer_email FROM Customer WHERE Customer_email = %s', (email,))
            if cursor.fetchone():
                return render_template('register.html', error='Email already registered')
            
            # Get the next available Customer_id
            cursor.execute('SELECT MAX(Customer_id) FROM Customer')
            result = cursor.fetchone()
            next_id = 1 if result[0] is None else result[0] + 1
            print(f"Generated Customer ID: {next_id}")  # Debug log
            
            # Insert new customer with plain text password
            insert_query = '''
                INSERT INTO Customer (Customer_id, Customer_name, Customer_email, Customer_contact_no, Customer_password)
                VALUES (%s, %s, %s, %s, %s)
            '''
            values = (next_id, name, email, contact, password)  # Store password directly
            print(f"Executing query: {insert_query} with values: {values}")  # Debug log
            
            cursor.execute(insert_query, values)
            conn.commit()
            print("Customer registered successfully")  # Debug log
            return redirect(url_for('login'))
            
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
            error_msg = f"Database error: {str(err)}"
            return render_template('register.html', error=error_msg)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            error_msg = f"An unexpected error occurred: {str(e)}"
            return render_template('register.html', error=error_msg)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/test_connection')
def test_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return 'Database connection successful!'
    except mysql.connector.Error as err:
        return f'Database connection failed: {err}'

@app.route('/customers')
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Customer')
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO Customer (Customer_id, Customer_name, Customer_email, Customer_contact_no, Customer_address)
                VALUES (%s, %s, %s, %s, %s)
            ''', (data['customer_id'], data['name'], data['email'], data['contact'], data['Customer_address']))
            conn.commit()
            return redirect(url_for('customers'))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return render_template('add_customer.html', error=str(err))
        finally:
            cursor.close()
            conn.close()
    return render_template('add_customer.html')

@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Product')
    products = cursor.fetchall()
    for product in products:
        print(f"Product image path: {product['Product_image']}")
    cursor.close()
    conn.close()
    # Only show Add to Cart buttons for customers
    is_customer = session.get('user_type') == 'customer'
    return render_template('products.html', products=products, is_customer=is_customer)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can add items to cart', 'error')
        return redirect(url_for('products'))
        
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity
    
    session.modified = True
    return redirect(url_for('products'))

@app.route('/cart')
def cart():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can view cart', 'error')
        return redirect(url_for('products'))
        
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total_price=0)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cart_items = []
    total_price = 0
    
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT * FROM Product WHERE Product_id = %s', (product_id,))
        product = cursor.fetchone()
        if product:
            product['quantity'] = quantity
            total_price += product['Product_price'] * quantity
            cart_items.append(product)
    
    cursor.close()
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can modify cart', 'error')
        return redirect(url_for('products'))
        
    product_id = request.form.get('product_id')
    if 'cart' in session and product_id in session['cart']:
        session['cart'].pop(product_id)
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can modify cart', 'error')
        return redirect(url_for('products'))
        
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        session['cart'].pop(product_id, None)
    else:
        session['cart'][product_id] = quantity
    
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/generate_bill/<int:order_id>')
def generate_bill(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get order details with customer information
        cursor.execute('''
            SELECT o.*, c.Customer_name, c.Customer_email, c.Customer_contact_no
            FROM Orders o
            LEFT JOIN Customer c ON o.Customer_id = c.Customer_id
            WHERE o.Order_id = %s
        ''', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('orders'))
            
        # Get order items with product details
        cursor.execute('''
            SELECT oi.*, p.Product_name, p.Product_price
            FROM Order_items oi
            JOIN Product p ON oi.Product_id = p.Product_id
            WHERE oi.Order_id = %s
        ''', (order_id,))
        order_items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('bill.html', 
                             order=order,
                             order_items=order_items,
                             date=datetime.now().strftime('%Y-%m-%d'))
                             
    except Exception as e:
        print(f"Error generating bill: {e}")
        flash('An error occurred while generating the bill.', 'error')
        return redirect(url_for('orders'))

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all orders with customer names and total amount
        if session.get('user_type') == 'customer':
            # For customers, only show their own orders
            cursor.execute('''
                SELECT o.Order_id, o.Order_date, o.Order_status, o.return_status,
                       o.Total_amount, o.Customer_id, 
                       IFNULL(c.Customer_name, 'Unknown') as Customer_name,
                       o.Shipping_address, o.Payment_method
                FROM Orders o
                LEFT JOIN Customer c ON o.Customer_id = c.Customer_id
                WHERE o.Customer_id = %s
                ORDER BY o.Order_date DESC
            ''', (session['user_id'],))
        else:
            # For employees, show all orders
            cursor.execute('''
                SELECT o.Order_id, o.Order_date, o.Order_status, o.return_status,
                       o.Total_amount, o.Customer_id, 
                       IFNULL(c.Customer_name, 'Unknown') as Customer_name,
                       o.Shipping_address, o.Payment_method
                FROM Orders o
                LEFT JOIN Customer c ON o.Customer_id = c.Customer_id
                ORDER BY o.Order_date DESC
            ''')
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('orders.html', orders=orders)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return f"An error occurred: {err}", 500
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while fetching orders.", 500

@app.route('/request_return/<int:order_id>', methods=['POST'])
def request_return(order_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can request returns', 'error')
        return redirect(url_for('orders'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the order exists and belongs to the customer
        cursor.execute('''
            SELECT Order_status, return_status 
            FROM Orders 
            WHERE Order_id = %s AND Customer_id = %s
        ''', (order_id, session['user_id']))
        order = cursor.fetchone()
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('orders'))
        
        if order['Order_status'] != 'Completed':
            flash('Only completed orders can be returned.', 'error')
            return redirect(url_for('orders'))
        
        if order['return_status']:
            flash('A return request already exists for this order.', 'error')
            return redirect(url_for('orders'))
        
        # Get return reason from form
        return_reason = request.form.get('return_reason')
        if not return_reason:
            flash('Please provide a reason for the return.', 'error')
            return redirect(url_for('orders'))
        
        # Update the order with return status and reason
        cursor.execute('''
            UPDATE Orders 
            SET return_status = 'Pending',
                return_reason = %s
            WHERE Order_id = %s
        ''', (return_reason, order_id))
        
        conn.commit()
        flash('Return request submitted successfully.', 'success')
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('An error occurred while processing your return request.', 'error')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('orders'))

@app.route('/process_return/<int:order_id>/<action>', methods=['POST'])
def process_return(order_id, action):
    if 'user_id' not in session or session.get('user_type') != 'employee':
        flash('Only employees can process returns', 'error')
        return redirect(url_for('orders'))
    
    if action not in ['approve', 'reject']:
        flash('Invalid action.', 'error')
        return redirect(url_for('orders'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the order exists and has a pending return
        cursor.execute('''
            SELECT return_status 
            FROM Orders 
            WHERE Order_id = %s
        ''', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('orders'))
        
        if order['return_status'] != 'Pending':
            flash('Only pending returns can be processed.', 'error')
            return redirect(url_for('orders'))
        
        # Update the return status
        new_status = 'Approved' if action == 'approve' else 'Rejected'
        cursor.execute('''
            UPDATE Orders 
            SET return_status = %s
            WHERE Order_id = %s
        ''', (new_status, order_id))
        
        conn.commit()
        flash(f'Return request {new_status.lower()} successfully.', 'success')
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('An error occurred while processing the return request.', 'error')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return redirect(url_for('orders'))

@app.route('/check_table_structure')
def check_table_structure():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DESCRIBE Customer')
        columns = cursor.fetchall()
        return jsonify(columns)
    except mysql.connector.Error as err:
        return f"Error: {err}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/remove_password_column')
def remove_password_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First, disable foreign key checks
        cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        
        # Remove the password column
        cursor.execute('ALTER TABLE Customer DROP COLUMN Customer_password')
        
        # Re-enable foreign key checks
        cursor.execute('SET FOREIGN_KEY_CHECKS=1')
        
        conn.commit()
        return "Successfully removed Customer_password column"
    except mysql.connector.Error as err:
        return f"Error: {err}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/check_employee_table')
def check_employee_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DESCRIBE Employee')
        columns = cursor.fetchall()
        return jsonify(columns)
    except mysql.connector.Error as err:
        return f"Error: {err}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can checkout', 'error')
        return redirect(url_for('products'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cart_items = []
        total_price = 0
        
        if 'cart' in session:
            for product_id, quantity in session['cart'].items():
                cursor.execute('SELECT * FROM Product WHERE Product_id = %s', (product_id,))
                product = cursor.fetchone()
                if product:
                    product['quantity'] = quantity
                    total_price += product['Product_price'] * quantity
                    cart_items.append(product)
        
        if not cart_items:
            flash('Your cart is empty.', 'error')
            return redirect(url_for('cart'))
        
        return render_template('payment.html', cart_items=cart_items, total_price=total_price)
    
    except mysql.connector.Error as err:
        print(f"Database error in checkout: {err}")
        flash('An error occurred while processing your checkout. Please try again.', 'error')
        return redirect(url_for('cart'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Only customers can place orders', 'error')
        return redirect(url_for('products'))
    
    conn = None
    cursor = None
    
    try:
        # Debug logging for cart contents
        print(f"DEBUG: Cart contents: {session.get('cart', {})}")
        print(f"DEBUG: User ID: {session.get('user_id')}")
        
        # Validate cart
        if not session.get('cart'):
            flash('Your cart is empty.', 'error')
            return redirect(url_for('cart'))
        
        # Get and validate form data with detailed logging
        required_fields = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'pincode': request.form.get('pincode'),
            'payment_method': request.form.get('payment_method')
        }
        
        print(f"DEBUG: Received form data: {required_fields}")
        
        # Check for missing fields
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            print(f"DEBUG: Missing required fields: {missing_fields}")
            flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('checkout'))
        
        # Create shipping address string
        shipping_address = f"{required_fields['full_name']}\n{required_fields['address']}\n{required_fields['city']}, {required_fields['state']} - {required_fields['pincode']}\nPhone: {required_fields['phone']}"
        
        # Connect to database
        print("DEBUG: Attempting database connection...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Calculate total amount first
            total_amount = 0
            cart_items = []
            
            print("DEBUG: Calculating total amount...")
            for product_id, quantity in session['cart'].items():
                # Convert product_id to integer if it's a string
                product_id = int(product_id)
                print(f"DEBUG: Processing product ID: {product_id}, Quantity: {quantity}")
                
                cursor.execute('SELECT Product_id, Product_name, Product_price FROM Product WHERE Product_id = %s', (product_id,))
                product = cursor.fetchone()
                
                if not product:
                    raise ValueError(f"Product with ID {product_id} not found")
                
                print(f"DEBUG: Product found: {product}")
                
                item_price = float(product['Product_price']) * int(quantity)
                total_amount += item_price
                cart_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': item_price
                })
            
            print(f"DEBUG: Total amount calculated: {total_amount}")
            
            # Get next Order_id
            cursor.execute('SELECT MAX(Order_id) as max_id FROM Orders')
            result = cursor.fetchone()
            next_order_id = 1 if result['max_id'] is None else result['max_id'] + 1
            print(f"DEBUG: Next Order ID: {next_order_id}")
            
            # Create order
            order_date = datetime.now().strftime('%Y-%m-%d')
            print("DEBUG: Creating order...")
            
            # Insert into Orders table
            insert_order_query = '''
                INSERT INTO Orders (Order_id, Order_date, Customer_id, Total_amount, Shipping_address, Payment_method, Order_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            order_values = (
                next_order_id,
                order_date,
                session['user_id'],
                total_amount,
                shipping_address,
                required_fields['payment_method'],
                'Pending' if required_fields['payment_method'] == 'cod' else 'Processing'
            )
            
            print(f"DEBUG: Executing order insert with values: {order_values}")
            cursor.execute(insert_order_query, order_values)
            print(f"DEBUG: Order created with ID: {next_order_id}")
            
            # Add order items
            print("DEBUG: Adding order items...")
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO Order_items (Order_id, Product_id, Quantity, Item_price)
                    VALUES (%s, %s, %s, %s)
                ''', (next_order_id, item['product_id'], item['quantity'], item['price']))
                
                print(f"DEBUG: Added order item for product {item['product_id']}")
            
            # Commit transaction
            conn.commit()
            print(f"DEBUG: Order {next_order_id} created successfully")
            
            # Clear the cart
            session.pop('cart', None)
            
            flash(f'Order #{next_order_id} placed successfully! Thank you for shopping with us.', 'success')
            return redirect(url_for('products'))
            
        except mysql.connector.Error as err:
            print(f"DEBUG: MySQL Error during transaction: {err}")
            if conn:
                conn.rollback()
            flash(f'Database error: {str(err)}', 'error')
            return redirect(url_for('cart'))
            
    except mysql.connector.Error as err:
        print(f"DEBUG: Database error: {err}")
        flash(f'Database error: {str(err)}', 'error')
        return redirect(url_for('cart'))
    except ValueError as err:
        print(f"DEBUG: Validation error: {err}")
        flash(str(err), 'error')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"DEBUG: Unexpected error: {type(e).__name__}: {str(e)}")
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('cart'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            try:
                conn.close()
                print("DEBUG: Database connection closed")
            except Exception as e:
                print(f"DEBUG: Error closing connection: {e}")

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'employee':
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get summary counts
        cursor.execute('SELECT COUNT(*) as customer_count FROM Customer')
        customer_count = cursor.fetchone()['customer_count']
        
        cursor.execute('SELECT COUNT(*) as product_count FROM Product')
        product_count = cursor.fetchone()['product_count']
        
        cursor.execute('SELECT COUNT(*) as order_count FROM Orders')
        order_count = cursor.fetchone()['order_count']
        
        # Get recent orders
        cursor.execute('''
            SELECT o.Order_id, o.Order_date, o.Order_status,
                   o.Total_amount, c.Customer_name
            FROM Orders o
            LEFT JOIN Customer c ON o.Customer_id = c.Customer_id
            ORDER BY o.Order_date DESC
            LIMIT 5
        ''')
        recent_orders = cursor.fetchall()
        
        # Get recent customers
        cursor.execute('''
            SELECT Customer_id, Customer_name, Customer_email, Customer_contact_no
            FROM Customer
            ORDER BY Customer_id DESC
            LIMIT 5
        ''')
        recent_customers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin_dashboard.html',
                             customer_count=customer_count,
                             product_count=product_count,
                             order_count=order_count,
                             recent_orders=recent_orders,
                             recent_customers=recent_customers)
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        return "An error occurred while loading the dashboard.", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000) 