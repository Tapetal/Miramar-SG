import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Read the SQL file
with open('pythonproject.sql', 'r') as f:
    sql_script = f.read()

# Execute the SQL commands
cursor.executescript(sql_script)

# Commit and close the connection
conn.commit()
conn.close()
