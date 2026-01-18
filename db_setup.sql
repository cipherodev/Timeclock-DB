BEGIN;

CREATE TABLE IF NOT EXISTS Employees (
    first_name TEXT,
    last_name TEXT,
    finger_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Employee_info (
    finger_id INTEGER PRIMARY KEY,
    absences INTEGER DEFAULT 0,
    tardies INTEGER DEFAULT 0,
    FOREIGN KEY(finger_id) REFERENCES Employees(finger_id)
);

CREATE TABLE IF NOT EXISTS timesheet (
    finger_id INTEGER,
    sign_in DATETIME,
    sign_out DATETIME,
    no_show INTEGER,
    FOREIGN KEY(finger_id) REFERENCES Employees(finger_id)
);

CREATE TABLE IF NOT EXISTS wifi (
    id INT DEFAULT 0,
    ssid TEXT,
    password TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    tardy_time TEXT DEFAULT '06:00:00' --HH:MM:SS
);