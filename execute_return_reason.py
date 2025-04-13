import mysql.connector

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'ecommerce_website',
}

def add_return_reason():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Add return_reason column
        cursor.execute('ALTER TABLE Orders ADD COLUMN return_reason TEXT DEFAULT NULL')
        
        conn.commit()
        print("Successfully added return_reason column to Orders table")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_return_reason() 