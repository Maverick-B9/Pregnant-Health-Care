-- smart-healthcare-app/database/schema.sql

-- Ensure the database exists and is selected.
-- You might need to create the database manually first: CREATE DATABASE smart_health_db;
USE smarthealthcare;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: diagnostics
-- MODIFIED: Added columns for all 8 input features if you wish to store them.
-- Choose which ones you actually want to store.
CREATE TABLE IF NOT EXISTS diagnostics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    pregnancies FLOAT,
    glucose FLOAT,
    bloodpressure FLOAT,
    skinthickness FLOAT,
    insulin FLOAT,
    bmi FLOAT,
    dpf FLOAT, -- Diabetes Pedigree Function
    age FLOAT,
    prediction_result FLOAT, -- Stores the predicted probability or percentage
    -- result_category VARCHAR(50), -- Optional: 'Low Risk', 'High Risk'
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL -- Or ON DELETE CASCADE
);

-- Table: health_records
CREATE TABLE IF NOT EXISTS health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(50), -- e.g., 'Routine', 'First Trimester'
    test_name VARCHAR(100), -- e.g., 'Hemoglobin'
    value_numeric FLOAT, -- For numerical results
    value_text TEXT, -- For text observations or qualitative results
    file_path VARCHAR(255), -- Path to uploaded report file
    test_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: chat_logs
CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_message TEXT,
    bot_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL -- Or ON DELETE CASCADE
);

CREATE TABLE daily_health_logs (
                                  id INT AUTO_INCREMENT PRIMARY KEY,
                                user_id INT NOT NULL,
                                log_date DATE NOT NULL,
                                sleep_hours FLOAT,
                                steps_count INT,
                                water_glasses INT,
                                mood_score INT,
                                gemini_insight TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users(id),
                                UNIQUE KEY unique_daily_log (user_id, log_date)
                                );
-- ADDED: Indexes for frequently queried columns for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_diagnostics_user_id ON diagnostics(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_user_id ON chat_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_health_logs_user_id ON daily_health_logs(user_id);