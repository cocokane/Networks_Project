DROP DATABASE IF EXISTS users;
CREATE DATABASE users;
USE users;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);

INSERT INTO users (name, email, password, role) VALUES
-- Additional users
INSERT INTO users (name, email, password, role) VALUES
    ('Deepanjali Kumari', 'deepanjali.kumari@iitgn.ac.in', '22110069', 'Visitor'),
    ('Harshita Singh', 'harshita.singh@iitgn.ac.in', '22110140', 'Staff'),
    ('Anushika Mishra', 'anushika.mishra@iitgn.ac.in', '22110029', 'Staff'),
    ('Yash Kokane', 'yash.kokane@iitgn.ac.in', '20110237', 'Admin'),
    
    -- Random users
    ('Ajay Verma', 'ajay.verma@gmail.com', '123456', 'patient'),
    ('Meera Nair', 'meera.nair@gmail.com', '123456', 'doctor'),
    ('Siddharth Rao', 'siddharth.rao@gmail.com', '123456', 'admin');

