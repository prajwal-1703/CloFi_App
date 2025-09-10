
CREATE DATABASE secure_donation_db;
USE secure_donation_db;


CREATE TABLE user (
    id INT(11) NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

-- Create need table
CREATE TABLE need (
    id INT(11) NOT NULL AUTO_INCREMENT,
    title VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_by INT(11),
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TABLE donation (
    id INT(11) NOT NULL AUTO_INCREMENT,
    donor_name VARCHAR(120) NOT NULL,
    item VARCHAR(120) NOT NULL,
    quantity INT(11) NOT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL,
    need_id INT(11),
    PRIMARY KEY (id),
    FOREIGN KEY (need_id) REFERENCES need(id) ON DELETE SET NULL
);
