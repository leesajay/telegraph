import csv
import sqlite3 as s

databaseInput = []

with open("zips.csv", "rU") as data:
    reader = csv.reader(data)
    for row in reader:
        databaseInput.append(row)

#create the table

# SQL = 'CREATE TABLE IF NOT EXISTS zips(City, Zip, County);'
# 
# conn = s.connect("../telegraph.db")
# cur = conn.cursor()
# cur.execute(SQL)
# conn.commit()
# cur.close()
# conn.close()

#populate the table

conn = s.connect("../telegraph.db")
conn.text_factory = str
cur = conn.cursor()
for item in databaseInput:
    if item != databaseInput[0]:
        SQL = "INSERT INTO zips VALUES(?, ?, ?);"
        cur.execute(SQL, item)
        conn.commit()
cur.close()
conn.close()


    
            

