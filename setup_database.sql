CREATE TABLE Payment (
    Pay_id INT PRIMARY KEY,
    Pay_mode VARCHAR(50),
    Pay_amt DECIMAL(10, 2),
    Pay_desc VARCHAR(255),
    Pay_date DATE
);

CREATE TABLE Customer (
    Customer_id INT PRIMARY KEY,
    Customer_name VARCHAR(100),
    Customer_email VARCHAR(100),
    Customer_contact_no VARCHAR(15),
    User_id INT,
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);


CREATE TABLE Orders (
    Order_id INT PRIMARY KEY,
    Order_date DATE,
    Customer_address VARCHAR(255),
    Total_amt DECIMAL(10, 2),
    Customer_id INT,
    FOREIGN KEY (Customer_id) REFERENCES Customer(Customer_id)
);

CREATE TABLE Order_Return (
    Return_amt DECIMAL(10, 2),
    Return_date DATE,
    Order_id INT,
    FOREIGN KEY (Order_id) REFERENCES Orders(Order_id)
);

CREATE TABLE Bill_Detail (
    Bill_id INT PRIMARY KEY,
    Pay_status VARCHAR(50),
    Bill_date DATE,
    Order_total_price DECIMAL(10, 2),
    Order_id INT,
    FOREIGN KEY (Order_id) REFERENCES Orders(Order_id)
);

CREATE TABLE Final_Bill_Detail (
    Order_tatal_price DECIMAL(10, 2),
    Offer_discount DECIMAL(10, 2),
    Bill_total_price DECIMAL(10, 2),
    Bill_id INT,
    FOREIGN KEY (Bill_id) REFERENCES Bill_Detail(Bill_id)
);

CREATE TABLE Product (
    Product_id INT PRIMARY KEY,
    Product_name VARCHAR(100),
    Product_qty INT,
    Product_colour VARCHAR(50),
    Product_price DECIMAL(10, 2)
);

alter table product
add column Product_image varchar(1000);

CREATE TABLE User (
    User_id INT PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    Password_hash VARCHAR(255) NOT NULL,
    Role VARCHAR(50) NOT NULL -- e.g., 'Customer', 'Employee'
);



CREATE TABLE Employee (
    Employee_id INT PRIMARY KEY,
    Employee_name VARCHAR(100),
    Employee_email VARCHAR(100),
    Employee_contact_no VARCHAR(15),
    Designation VARCHAR(100),
    User_id INT UNIQUE,
    FOREIGN KEY (User_id) REFERENCES User(User_id)
);

