import mysql.connector

# Database configuration (same as in app.py)
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'ecommerce_website',
}

try:
    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    # Execute the ALTER TABLE command
    cursor.execute('ALTER TABLE Customer ADD COLUMN Customer_password VARCHAR(64)')
    
    # Commit the changes
    connection.commit()
    print("Successfully added Customer_password column")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close() 