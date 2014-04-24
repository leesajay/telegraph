import csv
import sqlite3 as s

databaseInput = []

with open("forDatabase.csv", "rU") as data:
    reader = csv.reader(data)
    for row in reader:
        databaseInput.append(row)

# #create the table
# headers = ""
# for item in databaseInput[0]:
#     if item == databaseInput[0][0]:
#         headers += item
#     else:
#         headers += ", " + item
# 
# SQL = 'CREATE TABLE IF NOT EXISTS r(' + headers + ');'
# 
# conn = s.connect("telegraph.db")
# cur = conn.cursor()
# cur.execute(SQL)
# conn.commit()
# cur.close()
# conn.close()

#populate the table

conn = s.connect("telegraph.db")
conn.text_factory = str
cur = conn.cursor()
for item in databaseInput:
    if item != databaseInput[0]:
        SQL = "INSERT INTO r VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        cur.execute(SQL, item)
        conn.commit()
cur.close()
conn.close()


    
            

