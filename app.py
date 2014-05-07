#!/usr/bin/env python

from subprocess import check_output
import flask
import os
import sqlite3 as s
import itertools
import random
import string
from types import *
from flask import Flask,request, session, escape, redirect, jsonify

# create our little application
app = Flask(__name__)
app.debug=True

#helper function for getting database counts for a given field/filter
def answerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a dict of the answers as key and count as value)'''
    
    conn = s.connect("telegraph.db")
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
#helper function specific to the likert data structure needs of a list
def listAnswerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a list of answer counts in order that targetAnswers gives answers'''    

    conn = s.connect("telegraph.db")
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
    #print(pane1)
    
    return pane1
    
#helper function for makePane2() to collect random quotes
def getRandom(targetField):
    conn = s.connect("telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()

    responseID = str(random.randint(1,1108))
    SQL = "SELECT " + targetField + " FROM r WHERE ResponseID = ?;"
    data = (responseID,)
    cur.execute(SQL, data)
    candidate = cur.fetchone()[0]
    if len(candidate) > 0:
        cur.close()
        conn.close()
        if len(candidate) > 140:
            candidate = candidate.split(".", 1)[0]
        return candidate

    else: 
        return(getRandom(targetField))
        
def makePane2():
    '''makes the data object for the second, text-based pane'''    
    textData = []
    textData.append(getRandom("Like"))
    textData.append(getRandom("WishDifferent"))
    randomIdea = random.choice(["IdeasCars", "IdeasTransit", "IdeaseBikes", "IdeasPeds"])
    ideaText = getRandom(randomIdea)
    if randomIdea == "IdeasCars":
        textData.append("To improve Telegraph for cars: " + ideaText)
    if randomIdea == "IdeasTransit":
        textData.append("To improve Telegraph for public transit: " + ideaText)
    if randomIdea == "IdeaseBikes":
        textData.append("To improve Telegraph for bikes: " + ideaText) 
    if randomIdea == "IdeasPeds":
        textData.append("To improve Telegraph for pedestrians: " + ideaText)
        
    return textData

#pane 3 items
# 3a: frequency
def getFrequency():
     frequency = answerCount(("Daily", "A few times per week", "A few times per month", "Rarely"), "Frequency", "ResponseID", "IS NOT", '\"None\"') #those last parameters are just essentially dummies to satisfy the function
     # print(frequency)
     return frequency
     
# 3b: where do you live
def getLocation():
    location = {}
    conn = s.connect("telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    #gets count for responses in these three cities
    cities = ["Oakland", "Berkeley", "San Francisco"]
    for city in cities:
        SQL = 'SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip WHERE zips.City = ?;'
        data = (city,)    
        cur.execute(SQL, data)
        location[city] = cur.fetchone()[0]
    
    #gets count for these counties EXCLUDING the cities already counted 
    counties = ["Marin", "San Mateo", "Santa Clara", "Alameda", "Contra Costa"]
    for county in counties:
        SQL = '''SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip 
        WHERE zips.County = ? AND zips.City NOT IN ("Oakland", "Berkeley");'''
        data = (county,)
        cur.execute(SQL, data)
        count = cur.fetchone()[0]
        if county == "Alameda":
            location["Other Alameda County"] = count
        else:
            location[county + " County"] = count
    
    #gets count for other CA (all CA zips excluding those already counted)
    #NOTE THIS COUNT IS 0, JUST LIKE MARIN COUNTY, BUT DID NOT WANT TO DELETE (YET) 
    #TO BE CLEAR THAT QUERY HAS BEEN RUN!! 
    dataStr = "("
    for x in range(90001, 96162):
        dataStr += '\"' + str(x) + '\", '
    dataStr += '\"96162\")'
    SQL = '''SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip WHERE
     r.HomeZIP IN ''' + dataStr + ''' AND zips.City NOT IN ("Oakland", "Berkeley") AND
     zips.County NOT IN ("Marin", "San Mateo", "Santa Clara", "Alameda", "Contra Costa", "San Francisco");'''
    cur.execute(SQL)
    location["Other CA"] = cur.fetchone()[0]
    
    #gets count for other
    SQL = '''SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip WHERE
     zips.City IS NULL OR r.HomeZIP NOT IN ''' + dataStr + ';'
    cur.execute(SQL)
    location["Other"] = cur.fetchone()[0]
    
    #delete any location category with a 0 response count
    toDelete = [] #have to make a list of things to delete, otherwise Runtime Error: dictionary changed size during iteration
    for key, value in location.iteritems():
        if value == 0:
            toDelete.append(key)
    for item in toDelete:
        del location[item]

    cur.close()
    conn.close()
    return location

#for pane3c
# can't use answerCount() for this b/c of the slightly difft structure needed for the SQL statement
def getMode(priority):
    conn = s.connect("telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    mode = {}
    modes = ("%ACT%", "%BART%", "%Biking%", "%Driving%", "%Walking%", "%Other%")
    for item in modes:
        SQL = "SELECT COUNT(" + priority + ") from r WHERE " + priority + " LIKE ?;"
        data = (item,)
        cur.execute(SQL, data)
        count = cur.fetchone()[0]
        if item == "%Biking%":
            mode["Biking"] = count
        elif item == "%Driving%":
            mode["Driving"] = count
        elif item == "%Walking%":
            mode["Walking"] = count
        elif item == "%Other%":
            mode["Other"] = count
        else:
            mode[item] = count
        
    cur.close()
    conn.close()
    
    #add BART and ACT counts together to make one transit count
    transitTotal = mode["%ACT%"] + mode["%BART%"]
    mode["Transit"] = transitTotal
    del mode["%ACT%"]
    del mode["%BART%"]

    return mode
    
#for 3d, connection to Telegraph
#this could SO use refactoring to actually be extensible as intended, but NO TIME!
def makeVenn(setParams):
    '''takes list of lists where item[0] are fieldnames for set, item[1] are answers to be included in the set;
    not using a dict for this b/c order of items needs to be totally predictable to generate the overlaps;
    returns a list of lists: list[0] is a list sets where each set is a dict with a label and a size, like so: 
    [{label: "A", size: 10}, {label: "B", size: 10}]; list[1] is a list of overlaps like so: [{sets: [0,1], size: 2}]
    set labels will be added to the items by the list.index() method.'''
    
    conn = s.connect("telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    vennData = []
    sets = []
    overlaps = []
    #to get the sets, get the count for each field (key) with the proper answer (value)
    for pair in setParams:
        SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + pair[0] + "= ?;"
        data = (pair[1],)
        cur.execute(SQL, data)
        #make a dict entry in the format called for by the venn diagram library
        count = cur.fetchone()[0]
        if pair[0] == "Resident":
            setItem = {"label": "Live in a nearby neighborhood, " + str(count), "size": count}
        if pair[0] == "Business":
            setItem = {"label": "Own a business on Telegraph, " + str(count), "size": count}
        if pair[0] == "Work":
            setItem = {"label": "Work on or near Telegraph, " + str(count), "size": count}
        if pair[0] == "Visit":
            setItem = {"label": "Visit the shops, restaurants, and other businesses on Telegraph, " + str(count), "size": count}
        if pair[0] == "Commute":
            setItem = {"label": "Commute via Telegraph, " + str(count), "size": count}
        sets.append(setItem)
        pair.append(setParams.index(pair))
    vennData.append(sets)    
    
    for n in range(2, len(setParams) + 1):
        nCombos = itertools.combinations(setParams, n)
        for combo in nCombos:
            overlapEntry = {}
            if n == 2:
                 #first make a string of the right # of ?s and the column names
                SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + combo[0][0] + " = ? AND " + combo[1][0] + " = ?;"
                data = (combo[0][1], combo[1][1])
                cur.execute(SQL, data)
                count = cur.fetchone()[0]
                overlapEntry["sets"] = [combo[0][2], combo[1][2]]
                overlapEntry["size"] = count
                overlaps.append(overlapEntry)
            if n == 3:
                SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + combo[0][0] + " = ? AND " + combo[1][0] + " = ? AND " + combo[2][0] + " = ?;"
                data = (combo[0][1], combo[1][1], combo[2][1])
                cur.execute(SQL, data)
                count = cur.fetchone()[0]
                overlapEntry["sets"] = [combo[0][2], combo[1][2], combo[2][2]]
                overlapEntry["size"] = count
                overlaps.append(overlapEntry)
            if n == 4:
                SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + combo[0][0] + " = ? AND " + combo[1][0] + " = ? AND " + combo[2][0] + " = ? AND " + combo[3][0] + " = ?;"
                data = (combo[0][1], combo[1][1], combo[2][1], combo[3][1])
                cur.execute(SQL, data)
                count = cur.fetchone()[0]
                overlapEntry["sets"] = [combo[0][2], combo[1][2], combo[2][2], combo[3][2]]
                overlapEntry["size"] = count
                overlaps.append(overlapEntry)
            if n == 5:
                SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + combo[0][0] + " = ? AND " + combo[1][0] + " = ? AND " + combo[2][0] + " = ? AND " + combo[3][0] + " = ? AND " + combo[4][0] + " = ? ;"
                data = (combo[0][1], combo[1][1], combo[2][1], combo[3][1], combo[4][1])
                cur.execute(SQL, data)
                count = cur.fetchone()[0]
                overlapEntry["sets"] = [combo[0][2], combo[1][2], combo[2][2], combo[3][2], combo[4][2]]
                overlapEntry["size"] = count
                overlaps.append(overlapEntry)
    vennData.append(overlaps)
                        
    cur.close()
    conn.close()    
    return vennData

def vennReplace():
    conn = s.connect("telegraph.db")
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

    connectData = {"One connection only": one, "Two connections": two, "Three connections": three, "Four connections": four, "Five connections": five}
    return connectData
    
@app.route('/', methods=['GET'])
def sendToIndex():
    url = "http://groups.ischool.berkeley.edu/telegraph/index"
    return flask.redirect(url)

@app.route('/index', methods=['GET'])
#insert everything here
def load_page():
    app.logger.debug("page load called")
    pane1 = makePane1("'%'") 
    textData = makePane2()
    frequency = getFrequency()
    location = getLocation()
    primaryTransitData = getMode("Mode1")
    leastUsedTransitData = getMode("Mode6")
    teleConnection = vennReplace()
    filterValue = "'%'"
#     app.logger.debug("PANE 1 DATA")
#     app.logger.debug(pane1)
#     app.logger.debug("PANE 2 DATA")
#     app.logger.debug(textData)
#     app.logger.debug("PANE 3 DATA")
#     #app.logger.debug(frequency)
#     app.logger.debug(location)
#     #app.logger.debug(primaryTransitData)
#     #app.logger.debug(leastUsedTransitData)
#     #app.logger.debug(vennData)

    #variable syntax for render params is nameInTemplate = nameInApp.py
    return flask.render_template("index.html", 
                                    currentlySuitsData = pane1[0],
                                    highestPriorityData = pane1[1],
                                    lowestPriorityData = pane1[2],
                                    quoteData = textData,
                                    useFrequencyData = frequency,
                                    homeData = location,
                                    primaryTransitData = primaryTransitData, 
                                    leastUsedTransitData = leastUsedTransitData, 
                                    connectionToTeleData = teleConnection,
                                    dropdownValue = filterValue)

@app.route('/filtered', methods=['GET', 'POST'])
#insert everything here
def load_filtered_page():
    app.logger.debug("filtered page function called")
    if request.method == "POST":
        #take the filter from the form
        filterValue = request.form.get("filterValue")
    else: filterValue = "'%'"
    #now we are filtering on the proper data
    pane1 = makePane1(filterValue) 
    textData = makePane2()
    frequency = getFrequency()
    location = getLocation()
    primaryTransitData = getMode("Mode1")
    leastUsedTransitData = getMode("Mode6")
    teleConnection = vennReplace()
 #     app.logger.debug("PANE 1 DATA")
#     app.logger.debug(pane1)
#     app.logger.debug("PANE 2 DATA")
#     app.logger.debug(textData)
#     app.logger.debug("PANE 3 DATA")
#     #app.logger.debug(frequency)
#     app.logger.debug(location)
#     #app.logger.debug(primaryTransitData)
#     #app.logger.debug(leastUsedTransitData)
#     #app.logger.debug(vennData)

    #variable syntax for render params is nameInTemplate = nameInApp.py
    return flask.render_template("index.html", 
                                    currentlySuitsData = pane1[0],
                                    highestPriorityData = pane1[1],
                                    lowestPriorityData = pane1[2],
                                    quoteData = textData,
                                    useFrequencyData = frequency,
                                    homeData = location,
                                    primaryTransitData = primaryTransitData, 
                                    leastUsedTransitData = leastUsedTransitData, 
                                    connectionToTeleData = teleConnection,
                                    dropdownValue = filterValue)




app.secret_key = os.urandom(24)

if __name__ == "__main__":
	app.run(port=61008)
