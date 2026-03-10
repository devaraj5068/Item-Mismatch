-- Sample data for TrackRight

USE trackright_db;

-- Insert sample products
INSERT INTO core_product (name, sku, description, quantity) VALUES
('Widget A', 'WGT-A-001', 'A standard widget', 100),
('Widget B', 'WGT-B-002', 'An advanced widget', 50),
('Gadget C', 'GDT-C-003', 'A useful gadget', 75);

-- Insert sample orders
INSERT INTO core_order (order_number, customer_name, status) VALUES
('ORD-001', 'John Doe', 'pending'),
('ORD-002', 'Jane Smith', 'shipped');

-- Insert order items
INSERT INTO core_orderitem (order_id, product_id, quantity) VALUES
(1, 1, 10),
(1, 2, 5),
(2, 3, 20);