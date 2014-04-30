#!/usr/bin/env python

from subprocess import check_output
import flask
import os
import sqlite3
import random
import string
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
        data = (filterValue, item)
        #technically I know it's not "safe" to build SQL queries this way but b/c it's a SELECT and we are supplying the data I think it's ok
        SQL = "SELECT COUNT(" + targetField + ") from r WHERE " + filterField + " " + operator + " ? AND " + targetField + " = ?;" #gets count of each answer in the target field
        cur.execute(SQL, data)
        returnDict[item] = cur.fetchone()[0] #appends count to the list
    
    cur.close()
    conn.close()

    return returnDict


def makePane1(filterValue):
    '''makes and delivers data for the first pane of our viz'''
    pane1 = []
    filterField = "Mode1"
    operator = "LIKE"
    #for "Does current config work?" question
    configAnswers = ("Strongly Agree", "Agree", "No Opinion", "Disagree", "Strongly Disagree", "") 
    configTargets = ("GoodPeds", "GoodBikes", "GoodCars", "GoodTransit")
    configuration= {}
    for item in configTargets:
        configuration[item] = (answerCount(configAnswers, item, filterField, operator, filterValue))
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
    #I have tried many combos of different Booleans to exclude both None and '' and I can never get them both
    # excluded and I don't know why!!
    if not candidate == None: 
        cur.close()
        conn.close()
        return candidate
    else:
        getRandom(targetField)


def makePane2():
    '''makes the data object for the second, text-based pane'''    
    textData = []
    textData.append(getRandom("Like"))
    textData.append(getRandom("WishDifferent"))
    randomIdea = random.choice(["IdeasCars", "IdeasTransit", "IdeaseBikes", "IdeasPeds"])
    textData.append(randomIdea)
    textData.append(getRandom(randomIdea))
    return textData

#pane 3 items
# 3a: frequency
def getFrequency():
     frequency = answerCount(("Daily", "A few times per week", "A few times per month", "Rarely"), "Frequency", "ResponseID", "IS NOT", "None") #those last parameters are just essentially dummies to satisfy the function
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
        location[county + " County"] = cur.fetchone()[0]
    
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
# including empty string in the answers for now b/c I feel no response is maybe an illuminating data point for this
# can't use answerCount() for this b/c of the slightly difft structure needed for the SQL statement
def getMode(priority):
    conn = s.connect("telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()
    
    mode = {}
    modes = ("%ACT%", "%BART%", "%Biking%", "%Driving%", "%Walking%", "%Other%", "")
    for item in modes:
        SQL = "SELECT COUNT(" + priority + ") from r WHERE " + priority + " LIKE ?;"
        data = (item,)
        cur.execute(SQL, data)
        mode[item] = cur.fetchone()[0]
        
    cur.close()
    conn.close()
    
    #add BART and ACT counts together to make one transit count
    transitTotal = mode["%ACT%"] + mode["%BART%"]
    mode["Transit"] = transitTotal

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
        setItem = {"label": pair[0], "size": count}
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


@app.route('/')
#insert everything here
def welcome():
    app.logger.debug("welcome function called")
    #this param is a test value to prevent errors
    #what will go in here when we are ready is filterValue param
    #which  is passed from the front-end form and needs to be wrapped in %
    pane1 = makePane1("%Biking%") 
    textData = makePane2()
    frequency = getFrequency()
    location = getLocation()
    primaryTransitData = getMode("Mode1")
    leastUsedTransitData = getMode("Mode6")
    tgraphConnection = [["Resident", "Yes"], ["Business", "Yes"], ["Work", "Yes"], ["Visit", "Yes"], ["Commute", "Yes"]]
    vennData = (makeVenn(tgraphConnection))

    #variable syntax for render params is nameInTemplate = nameInApp.py
    return flask.render_template("index.html", 
                                    currentlySuitsData = pane1[0],
                                    highestPriorityData = pane1[1],
                                    lowestPriorityData = pane1[2],
                                    loveQuoteData = textData[0],
                                    hateQuoteData = textData[1],
                                    randomQuoteData = textData[2],
                                    useFrequencyData = frequency,
                                    homeData = location,
                                    primaryTransitData = primaryTransitData, 
                                    leastUsedTransitData = leastUsedTransitData, 
                                    connectionToTeleData = vennData)


app.secret_key = os.urandom(24)

if __name__ == "__main__":
	app.run(port=61008)	
