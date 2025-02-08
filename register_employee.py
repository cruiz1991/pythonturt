import sqlite3

def add_employee(name,position):
    conn=sqlite3.connect('attendance.db')
    cursor=conn.cursor()

    cursor.execute("INSERT INTO employees (name, position) VALUES (?, ?)", (name, position))
    conn.commit()
    conn.close()

    print(f'employees {name} added successfully')

    # example usage
    # 
    # 
    
    # Prints the databased employee

def print_employees():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    print("Employees in database:", employees)
    conn.close()


    # 
if __name__ == '__main__':
    name = input('Enter employee name: ')
    position= input('What is your position: ')
    add_employee(name, position)
    
    
        # Query to verify the employees in the database

    conn=sqlite3.connect('attendance.db')
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees =cursor.fetchall()
    print(employees)

conn.close()    