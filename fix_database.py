import mysql.connector

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'ecommerce_website',
}

def fix_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS Order_items")
        cursor.execute("DROP TABLE IF EXISTS Orders")
        
        # Create Orders table
        cursor.execute("""
            CREATE TABLE Orders (
                Order_id INT PRIMARY KEY AUTO_INCREMENT,
                Customer_id INT NOT NULL,
                Order_date DATETIME NOT NULL,
                Total_amount DECIMAL(10,2) DEFAULT 0.00,
                Shipping_address TEXT,
                Payment_method VARCHAR(50),
                Order_status VARCHAR(20) DEFAULT 'Pending',
                FOREIGN KEY (Customer_id) REFERENCES Customer(Customer_id)
            ) ENGINE=InnoDB
        """)
        print("Created Orders table")
        
        # Create Order_items table
        cursor.execute("""
            CREATE TABLE Order_items (
                Order_item_id INT PRIMARY KEY AUTO_INCREMENT,
                Order_id INT NOT NULL,
                Product_id INT NOT NULL,
                Quantity INT NOT NULL,
                Item_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (Order_id) REFERENCES Orders(Order_id),
                FOREIGN KEY (Product_id) REFERENCES Product(Product_id)
            ) ENGINE=InnoDB
        """)
        print("Created Order_items table")
        
        conn.commit()
        print("Database structure fixed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_database() 