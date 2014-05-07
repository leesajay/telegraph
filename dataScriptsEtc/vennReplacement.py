import sqlite3 as s
import itertools

#output i need here is to like the other bar charts:
#{"column label": count, "column label": count}

#call the database, get all the connection columns and then count the # of yesses in each response

def vennReplace():
    conn = s.connect("../telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    cur.execute("SELECT Resident, Business, Work, Visit, Commute FROM r;")
    responses = cur.fetchall()
    cur.close()
    conn.close()
        
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0

    for line in responses:
        count = 0
        for i in range(5):
            if line[i] == "Yes":
                count += 1
        if count == 1:
            one += 1
        if count == 2:
            two += 1
        if count == 3:
            three += 1
        if count == 4:
            four += 1
        if count == 5:
            five += 1
#     print("one: ", one)
#     print("two: ", two)
#     print("three: ", three)
#     print("four: ", four)
#     print("five: ", five)
#     print("sanity check")
#     print(one + two + three + four + five)

    connectData = {"One connection only": one, "Two connections": two, "Three connections": three, "Four connections": four, "Five connections": five}
    return connectData
    
vennReplace()
    
    


