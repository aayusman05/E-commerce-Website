ALTER TABLE Orders
ADD COLUMN Shipping_address TEXT,
ADD COLUMN Payment_method VARCHAR(50),
ADD COLUMN Order_status VARCHAR(20) DEFAULT 'Pending';

-- Update existing orders with default values
UPDATE Orders SET 
    Payment_method = 'Not Specified',
    Order_status = 'Completed'
WHERE Payment_method IS NULL; 