-- Initialize Paksa Financial System Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tenant table
CREATE TABLE IF NOT EXISTS tenant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default tenant
INSERT INTO tenant (id, name, code) VALUES 
('12345678-1234-5678-9012-123456789012', 'Paksa Demo Company', 'DEMO001')
ON CONFLICT (code) DO NOTHING;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo user (password: admin123)
INSERT INTO users (id, tenant_id, username, email, password_hash, first_name, last_name) VALUES 
('87654321-4321-8765-2109-876543210987', '12345678-1234-5678-9012-123456789012', 'admin', 'admin@paksa.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'Admin', 'User')
ON CONFLICT (username) DO NOTHING;

-- GL Accounts
CREATE TABLE IF NOT EXISTS gl_account (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, account_code)
);

-- Insert sample accounts
INSERT INTO gl_account (tenant_id, account_code, account_name, account_type) VALUES 
('12345678-1234-5678-9012-123456789012', '1000', 'Cash', 'Asset'),
('12345678-1234-5678-9012-123456789012', '1200', 'Accounts Receivable', 'Asset'),
('12345678-1234-5678-9012-123456789012', '2000', 'Accounts Payable', 'Liability'),
('12345678-1234-5678-9012-123456789012', '4000', 'Revenue', 'Revenue'),
('12345678-1234-5678-9012-123456789012', '5000', 'Expenses', 'Expense')
ON CONFLICT (tenant_id, account_code) DO NOTHING;

-- Vendors
CREATE TABLE IF NOT EXISTS ap_vendor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    vendor_code VARCHAR(50) NOT NULL,
    vendor_name VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, vendor_code)
);

-- Insert sample vendors
INSERT INTO ap_vendor (tenant_id, vendor_code, vendor_name, email) VALUES 
('12345678-1234-5678-9012-123456789012', 'VEND001', 'Office Supplies Inc', 'billing@officesupplies.com'),
('12345678-1234-5678-9012-123456789012', 'VEND002', 'Tech Solutions Ltd', 'accounts@techsolutions.com')
ON CONFLICT (tenant_id, vendor_code) DO NOTHING;

-- Customers
CREATE TABLE IF NOT EXISTS ar_customer (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    customer_code VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    credit_limit DECIMAL(18,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, customer_code)
);

-- Insert sample customers
INSERT INTO ar_customer (tenant_id, customer_code, customer_name, email, credit_limit) VALUES 
('12345678-1234-5678-9012-123456789012', 'CUST001', 'ABC Corporation', 'billing@abccorp.com', 50000.00),
('12345678-1234-5678-9012-123456789012', 'CUST002', 'XYZ Industries', 'accounts@xyzind.com', 75000.00)
ON CONFLICT (tenant_id, customer_code) DO NOTHING;

-- Employees
CREATE TABLE IF NOT EXISTS employee (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenant(id),
    employee_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    hire_date DATE NOT NULL,
    salary DECIMAL(18,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, employee_id)
);

-- Insert sample employees
INSERT INTO employee (tenant_id, employee_id, first_name, last_name, email, department, position, hire_date, salary) VALUES 
('12345678-1234-5678-9012-123456789012', 'EMP001', 'John', 'Smith', 'john.smith@paksa.com', 'Finance', 'Accountant', '2023-01-15', 65000.00),
('12345678-1234-5678-9012-123456789012', 'EMP002', 'Sarah', 'Johnson', 'sarah.johnson@paksa.com', 'HR', 'HR Manager', '2023-02-01', 75000.00)
ON CONFLICT (tenant_id, employee_id) DO NOTHING;