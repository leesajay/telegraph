#writing a new function in a difft file is easier than trying to do it in the app.py file
#b/c of testing, printing etc

import sqlite3 as s

def answerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a dict of the answers as key and count as value)'''
    
    conn = s.connect("../telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()

    returnDict = {}
    for item in targetAnswers:
        data = (item,)
        #technically I know it's not "safe" to build SQL queries this way but b/c it's a SELECT and we are supplying the data I think it's ok
        SQL = "SELECT COUNT(" + targetField + ") from r WHERE " + filterField + " " + operator + " " + filterValue + " AND " + targetField + " = ?;" #gets count of each answer in the target field
        cur.execute(SQL, data)
        returnDict[item] = cur.fetchone()[0] #appends count to the list
    
    cur.close()
    conn.close()

    return returnDict


def listAnswerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a list of answer counts in order that targetAnswers gives answers'''    

    conn = s.connect("../telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    returnList = []
    for item in targetAnswers:
        data = (item,)
        SQL = "SELECT COUNT(" + targetField + ") from r WHERE " + filterField + " " + operator + " " + filterValue + " AND " + targetField + " = ?;" #gets count of each answer in the target field
        cur.execute(SQL, data)
        count = cur.fetchone()[0]
        returnList.append(count)
        
    cur.close()
    conn.close()
    
    return returnList
        
def makePane1(filterValue):
    '''makes and delivers data for the first pane of our viz'''
     #the js wants this format for the likert data:
     #data = [{"key": "Pedestrians", "values": [answer counts from neg to pos], "key": "Cars", "values": [counts]}]
    pane1 = []
    filterField = "Mode1"
    operator = "LIKE"
    #for "Does current config work?" question
    configAnswers = ("Strongly Disagree", "Disagree", "No Opinion", "Agree", "Strongly Agree") 
    configTargets = ("GoodPeds", "GoodBikes", "GoodCars", "GoodTransit")
    configuration= []
    for item in configTargets:
        itemDict = {}
        if item == "GoodPeds":
            itemDict["key"] = "Pedestrians"
            itemDict["values"] = listAnswerCount(configAnswers, item, filterField, operator, filterValue)
            configuration.append(itemDict)
            print(itemDict)
        if item == "GoodBikes":
            itemDict["key"] = "Bicyclists"
            itemDict["values"] = listAnswerCount(configAnswers, item, filterField, operator, filterValue)
            configuration.append(itemDict)
            print(itemDict)
        if item == "GoodCars":
            itemDict["key"] = "Drivers"
            itemDict["values"] = listAnswerCount(configAnswers, item, filterField, operator, filterValue)
            configuration.append(itemDict)
            print(itemDict)
        if item == "GoodTransit":
            itemDict["key"] = "Transit riders"
            itemDict["values"] = listAnswerCount(configAnswers, item, filterField, operator, filterValue)
            configuration.append(itemDict)
            print(itemDict)

#     print(configuration)
    pane1.append(configuration)

    #for the highest priority improvements chart
    priorityAnswers = ("Biking", "Driving", "Transit", "Walking")
    hiPri = answerCount(priorityAnswers, "Improve1", filterField, operator, filterValue)
    #print(hiPri)
    pane1.append(hiPri)
    #print(graphData)

    #for the lowest priority improvements chart
    loPri = answerCount(priorityAnswers, "Improve4", filterField, operator, filterValue)
    #print(loPri)
    pane1.append(loPri)
    print(pane1)
    
    return pane1
    


# filterField = "Mode1"
# operator = "LIKE"
# #for "Does current config work?" question
# targetAnswers = ("Strongly Disagree", "Disagree", "No Opinion", "Agree", "Strongly Agree") 
# targetFields = "GoodPeds"
# filterValue = "%Biking%"
# 
# print(listAnswerCount(targetAnswers, targetField, filterField, operator, filterValue))

makePane1("'%Biking%'")