import sqlite3
import os

data_types = '''
NULL: null value
INTEGER: Integer value
REAL: 8-byte floating point number
TEXT: Text with UTF encoding
BLOB: Blob-Data (stored like input)
BOOLEAN: Will be stored as Integer (0 for false, 1 for true)
'''

def check_path(path: str) -> bool:
    'Checks if path exists.'
    return os.path.exists(path)

def load(path: str) -> any:
    'Loads data from path and returns it.'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
            
    except FileNotFoundError:
        return f"The file at path '{path}' does not exist."
    except PermissionError:
        return f"Permission denied when trying to open the file at path '{path}'."
    except Exception as e:
        return f"An error occurred while loading the file at path '{path}': {e}"

class SQLSON:
    '''Manages a SQLite database.'''
    def __init__(self, db_path: str, db_setup_path: str=None):
        self.db_path = db_path
        self.db_setup_path = db_setup_path
        
    def init(self):
        '''Initializes database and runs db_setup.'''
        if self.db_setup_path is None:
            return
        if check_path(self.db_setup_path) != True:
            raise FileNotFoundError(f'Database setup file not found: {self.db_setup_path}')

        db_script = load(self.db_setup_path)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.executescript(db_script)
        conn.commit()
        cur.close()
        conn.close()

    def insert(self, table: str, data: dict):
        '''Inserts data into a table.'''
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        columns = ', '.join(data.keys())  # Get column names
        placeholders = ', '.join(['?'] * len(data))

        script = f'''
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
        '''
        cur.execute(script, tuple(data.values())) 
        conn.commit()
        cur.close()
        conn.close()


    def update(self, table: str, data: dict, where_col: str, where_val):
        '''Updates data in a table based on a condition.'''
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        set_clause = ', '.join([f'{k} = ?' for k in data.keys()])

        script = f'''
            UPDATE {table} 
            SET {set_clause} 
            WHERE {where_col} = ?
        '''

        values = tuple(data.values()) + (where_val,)

        cur.execute(script, values)
        conn.commit()
        cur.close()
        conn.close()


    def select(self, table: str, where: str=None) -> list:
        '''Selects data from a table.'''
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
       
        script = f'''
        SELECT * FROM {table}
        WHERE {where}
        '''

        cur.execute(script)
        data = cur.fetchall()
        cur.close()
        conn.close()

        return data
    
    def delete(self, table: str, where: str):
        '''Deletes data from a table.'''
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('PRAGMA foreign_keys = ON;') # In case foreign key

        script = f'''
        DELETE FROM {table}
        WHERE {where}
        '''
        cur.execute(script)
        conn.commit()
        cur.close()
        conn.close()

    def create_table(self, table: str, columns: dict):
        '''
        Creates a table.\n
        columns format: {'column_name': 'data_type',...}
        '''
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        script = f'''
        CREATE TABLE {table} (
            {', '.join([f'{k} {v}' for k, v in columns.items()])}
        )
        '''

        cur.execute(script)
        conn.commit()
        cur.close()
        conn.close()