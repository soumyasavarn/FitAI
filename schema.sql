CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR,
    time_joined TIMESTAMP,
    curr_weight DECIMAL(12,2),
    target_weight DECIMAL(12,2),
    height DECIMAL(12,2),
    gender VARCHAR(255),
    age INTEGER
);
CREATE TABLE IF NOT EXISTS calorie_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    calories INTEGER,
    date_log TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS weight_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    weight DECIMAL(12,2),
    date_log TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS illness_details (
    id INTEGER PRIMARY KEY,
    illness_name VARCHAR(255),
    chronic BOOLEAN
);
CREATE TABLE IF NOT EXISTS user_illness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    illness_id INTEGER,
    user_id INTEGER,
    severity INTEGER,
    FOREIGN KEY (illness_id) REFERENCES illness_details(id)
    FOREIGN KEY (user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS exercise_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    steps INTEGER,
    date_log TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS fitness_plan_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    r_steps INTEGER,
    r_calories INTEGER,
    r_mins_activity INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(id)
);