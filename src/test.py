import json
from employee_db import EmployeeDB 

# Initialize database
db = EmployeeDB("test_employees.db", 'db_setup.sql')
db.init()

# Test adding an employee
add_request = {
    "cmd": "add_employee",
    "first_name": "John",
    "last_name": "Doe",
    "finger_id": 123
}
print("Adding employee:", db.process_request(add_request))

# Test retrieving employee info
info_request = {"finger_id": 123}
print("Employee info:", db.get_employee_info(info_request))

# Test deleting the employee
del_request = {"cmd": "del_employee", "finger_id": 123}
print("Deleting employee:", db.process_request(del_request))

# Test updating WiFi settings
wifi_request = {
    "cmd": "wifi",
    "ssid": "TestNetwork",
    "password": "SecurePass123"
}
print("Updating WiFi:", db.process_request(wifi_request))