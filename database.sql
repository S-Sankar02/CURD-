
CREATE DATABASE ai;

USE ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email, phone, password, role)
VALUES
('Admin', 'admin@example.com', '9999999999', 'admin123', 'admin');

UPDATE users
SET role = 'admin'
WHERE email = 'admin@example.com';

SELECT * FROM users;
DESCRIBE users;
SHOW CREATE TABLE users;


ALTER TABLE users
MODIFY password VARCHAR(255) NOT NULL;