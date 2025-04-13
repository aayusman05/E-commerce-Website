ALTER TABLE Orders
ADD COLUMN return_status VARCHAR(20) DEFAULT NULL;

-- Update existing orders with default values
UPDATE Orders SET 
    return_status = NULL
WHERE return_status IS NULL; 