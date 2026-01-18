import json
from datetime import datetime
from sqlson  import SQLSON

class EmployeeDB(SQLSON):
    def __init__(self, db_path: str, sql_script_path: str=None):
        super().__init__(db_path, sql_script_path)

    def process_request(self, request: json) -> json:
        cmd =  request.get('cmd')
        match cmd:
            case 'timekeeper':
                return self.timekeeper(request)
            case 'add_employee':
                return self.add_employee(request)
            case 'del_employee':
                return self.del_employee(request)
            case 'wifi':
                return self.wifi(request)
            case _:
                return json.dumps({'received': False, 'error': f'Unknown command: {cmd}'})
            
    def timekeeper(self, request: json) -> json:
        '''
        Sign in/sign out the employee, Marks the employee as tardy if needed\n
        Updates Employee_info but not timesheet
        Args:
            finger_id: The finger id of the employee
            sign_in: The time the employee signed in, DATETIME FORMAT
        
        Returns:
            request (json): 
            - first_name (str)
            - last_name (str)
            - tardies (int)
            - absences (int)
            '''
        sign_in = request.get('sign_in')
        sign_out = request.get('sign_out')

        info = self.get_employee_info(request)

        finger_id = info.get('finger_id')
        first_name = info.get('first_name')
        last_name = info.get('last_name')
        absences = info.get('absences')
        tardies = info.get('tardies')

        tardy = False
        if sign_in and sign_out == None: # Sign out MUST be none, no double tardies
            tardy = self.tardy(request)
        if tardy:
            tardies = (tardies or 0) + 1 # Incase its None
            self.update('Employee_info', {'tardies': tardies}, 'finger_id', finger_id)


        request['tardies'] = tardies
        request['absences'] = absences
        request['first_name'] = first_name
        request['last_name'] = last_name
        return request
        
    def add_employee(self, request: json) -> json:
        '''
        Adds an employee to the database.
        
        Args:
            first_name: The first name of the employee.
            last_name: The last name of the employee.
            finger_id: The finger id of the employee.
            
        Returns:
            received (bool): The request object
            '''
        first_name = request.get('first_name')
        last_name = request.get('last_name')
        finger_id = request.get('finger_id')

        if (first_name is None or last_name is None) or finger_id is None:
            return json.dumps({'received': False, 'error': 'Missing required fields'})

        emp_data = {
            'first_name': first_name,
            'last_name': last_name,
            'finger_id': finger_id
        }

        info_data = {
            'Absences': 0,
            'tardies': 0,
            'finger_id': finger_id
        }
        self.insert('Employees', emp_data)
        self.insert('Employee_info', info_data)

        request['received'] = True
        return request

    def del_employee(self, request: json) -> json:
        '''
        PERMANTALY Deletes an employee from the database
        
        Args:
            finger_id: The finger id of the employee.
            
        Returns:
            received (bool): The request object
            '''
        finger_id = self.get_employee_info(request).get('finger_id')
        self.delete('Employee_info', f'finger_id={finger_id}')
        self.delete('Employees', f'finger_id={finger_id}')

        request['received'] = True
        return request

    def wifi(self, request: json) -> json:
        '''Updates the ssid and password of wifi.'''
        ssid = request.get('ssid')
        password = request.get('password')

        if ssid is None or password is None:
            return json.dumps({'received': False, 'error': 'Missing required fields'})
        
        self.update('Wifi', {'ssid': ssid, 'password': password}, 'id', 0)


        request['received'] = True
        return request
    
    def get_employee_info(self, request: json) -> json:
        '''
        Get from employee_info table from full name or finger_id
        Returns:
            request (json):
            - finger_id (int)
            - first_name (str)
            - last_name (str)
            - absences (int)
            - tardies (int)
            '''
        first_name = request.get('first_name')
        last_name = request.get('last_name')
        finger_id = request.get('finger_id')

        if finger_id == None:
            if not self.select('Employee_info', f'finger_id={finger_id}'):
                return {'error': 'Employee not found.'}
            _, _, finger_id = self.select('Employees', f"first_name='{first_name}' AND last_name='{last_name}'")[0] # What if multiple?
            request['finger_id'] = finger_id
        
        elif first_name == None and last_name == None:
            if not self.select('Employee_info', f'finger_id={finger_id}'):
                return {'error': 'Employee not found.'}
            first_name, last_name, _ = self.select('Employees', f'finger_id={finger_id}')[0]
            request['first_name'] = first_name
            request['last_name'] = last_name

        else:
            return json.dumps({'error': 'Could not get employee info. All is None or missing name.'})
        print(self.select('Employee_info', f'finger_id={finger_id}')[0])
        _, absences, tardies = self.select('Employee_info', f'finger_id={finger_id}')[0]
        request['absences'] = absences
        request['tardies'] = tardies
        return request

    def tardy(self, request: dict) -> bool:
        '''
        Checks if the employee is tardy. DOES NOT UPDATE THE DATABASE.
        
        Args:
            request: Dictionary containing:
                - sign_in (str or datetime): The time the employee signed in.
        
        Returns:
            bool:
            - True: Tardy.
            - False: Not tardy.
        '''
        sign_in_raw = request.get('sign_in')

        if isinstance(sign_in_raw, datetime):
            sign_in_str = sign_in_raw.strftime('%H:%M:%S')  
        else:
            sign_in_str = sign_in_raw 

        sign_in = datetime.strptime(sign_in_str, '%H:%M:%S')
        result = self.select('settings', 'tardy_time')
        
        if result:
            tardy_time_str = result[0][0]  
        else:
            tardy_time_str = '06:00:00' 

        tardy_time = datetime.strptime(tardy_time_str, '%H:%M:%S')

        return sign_in > tardy_time




        