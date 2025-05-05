-- SQLite compatible SQL Dump

-- Drop existing tables
DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rooms;

-- Create admin_users table
CREATE TABLE admin_users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  Username TEXT NOT NULL,
  Email TEXT NOT NULL,
  Password TEXT NOT NULL,
  password_reset_token TEXT NOT NULL,
  Role TEXT NOT NULL DEFAULT 'admin'
);

-- Insert data into admin_users
INSERT INTO admin_users (id, Username, Email, Password, password_reset_token, Role) VALUES
(1, 'ashraf', 'aminuashraf55@gmail.com', 'aminuashraf55@gmail.com', '', 'admin');

-- Create bookings table
CREATE TABLE bookings (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  room_name TEXT NOT NULL,
  check_in DATE NOT NULL,
  check_out DATE NOT NULL,
  no_of_guests INTEGER NOT NULL,
  room_type TEXT NOT NULL,
  price TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert data into bookings
INSERT INTO bookings (id, name, email, room_name, check_in, check_out, no_of_guests, room_type, price, status, created_at) VALUES
(4, 'apo', 'apo@gmail.com', 'Deluxe Ocean View', '2024-09-04', '2024-09-01', 4, 'AC', '$299.99', 'Confirmed', '2024-09-10 16:22:37'),
(5, 'aptech', 'aptech@gmail.com', 'Luxury Escape Room', '2024-09-24', '2024-09-12', 3, 'Single Bed', '$129.99', 'Confirmed', '2024-09-10 17:04:20'),
(6, 'sem', 'sem@gmail.com', 'Deluxe Ocean View', '2024-09-22', '2024-09-20', 2, 'Double Bed', '$299.99', 'Canceled', '2024-09-10 18:59:20');

-- Create rooms table
CREATE TABLE rooms (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  price REAL NOT NULL,
  image TEXT NOT NULL,
  description TEXT DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  Username TEXT NOT NULL,
  Email TEXT NOT NULL,
  Password TEXT NOT NULL,
  password_reset_token TEXT DEFAULT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);

-- Insert data into users
INSERT INTO users (id, Username, Email, Password, password_reset_token, role) VALUES
(2, 'apo', 'apo@gmail.com', 'apo@gmail.com', '9QDXiJmrN5wfWLOOidrbrg', 'user'),
(5, 'aptech', 'aptech@gmail.com', 'aptech@gmail.com', NULL, 'user'),
(6, 'sem', 'sem@gmail.com', 'sem@gmail.com', NULL, 'user');