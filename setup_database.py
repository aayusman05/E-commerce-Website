import mysql.connector

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'ecommerce_website',
}

def setup_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create or modify Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                Order_id INT PRIMARY KEY AUTO_INCREMENT,
                Customer_id INT,
                Order_date DATETIME,
                Total_amount DECIMAL(10,2),
                Shipping_address TEXT,
                Payment_method VARCHAR(50),
                Order_status VARCHAR(20) DEFAULT 'Pending',
                FOREIGN KEY (Customer_id) REFERENCES Customer(Customer_id)
            )
        ''')
        
        # Create Order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Order_items (
                Order_item_id INT PRIMARY KEY AUTO_INCREMENT,
                Order_id INT,
                Product_id INT,
                Quantity INT,
                Item_price DECIMAL(10,2),
                FOREIGN KEY (Order_id) REFERENCES Orders(Order_id),
                FOREIGN KEY (Product_id) REFERENCES Product(Product_id)
            )
        ''')
        
        conn.commit()
        print("Database tables created successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database() 