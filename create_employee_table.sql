-- Add password column to Customer table if it doesn't exist
ALTER TABLE Customer ADD COLUMN IF NOT EXISTS Customer_password VARCHAR(64);

-- Create Employee table
CREATE TABLE IF NOT EXISTS Employee (
    Employee_id INT AUTO_INCREMENT PRIMARY KEY,
    Employee_name VARCHAR(100) NOT NULL,
    Employee_email VARCHAR(100) NOT NULL UNIQUE,
    Employee_password VARCHAR(64) NOT NULL,
    Employee_role VARCHAR(50) DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 