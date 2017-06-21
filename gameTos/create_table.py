import sqlite3

conn = sqlite3.connect('database.db')
print "Opened database successfully";

conn.execute('''CREATE TABLE users (
				userId INTEGER PRIMARY KEY AUTOINCREMENT,
				username varchar(128) NOT NULL,
				password varchar(512) NOT NULL,
				token varchar(10) NOT NULL
				);''')
print "Table created successfully";
conn.close()