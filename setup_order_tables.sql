-- First, create or modify the Orders table
CREATE TABLE IF NOT EXISTS Orders (
    Order_id INT PRIMARY KEY AUTO_INCREMENT,
    Customer_id INT,
    Order_date DATETIME,
    Total_amount DECIMAL(10,2),
    Shipping_address TEXT,
    Payment_method VARCHAR(50),
    Order_status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Customer_id) REFERENCES Customer(Customer_id)
);

-- Then, create the Order_items table
CREATE TABLE IF NOT EXISTS Order_items (
    Order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    Order_id INT,
    Product_id INT,
    Quantity INT,
    Item_price DECIMAL(10,2),
    FOREIGN KEY (Order_id) REFERENCES Orders(Order_id),
    FOREIGN KEY (Product_id) REFERENCES Product(Product_id)
); 