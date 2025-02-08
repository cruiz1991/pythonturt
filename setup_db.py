import sqlite3
# help(sqlite3)
# connect to the database

conn= sqlite3.connect('attendance.db')
cursor=conn.cursor()



# create employee table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT NOT NULL
)
""")


# create attendance table

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    punch_in_time TEXT,
    punch_out_time TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees (id)
)
""")

conn.commit()
conn.close()

print()