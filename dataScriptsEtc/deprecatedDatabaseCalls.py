import sqlite3 as s
import random
import itertools

#first, a constructor/helper function used by the other functions that actually make the data passed to the front end
def answerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a dict of the answers as key and count as value)'''
    
    conn = s.connect("../telegraph.db")
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

    
# PANE 1: Is current config good for <mode of transit>, plus high and low priority modes for improvement
# Description/output
# Filtered on primary transit mode
#     Current config is good for--list of the following lists
    #     Peds--list of values (count of responses) for each answer (strongly agree, agree, no opinion, disagree, strongly disagree, null)
    #     bikes--list of values for each answer
    #     cars--list of values for each answer
    #     transit--list of values for each answer
#     Highest priority for improvements--list of values (count of responses) for each cars, bikes, peds, transit
#     Lowest priority for improvements--list of values for each of cars, bikes, peds, transit

# Pseudocode
# initialize lists for peds, bikes, cars, transit, highPriority and lowPriority
# for each mode (peds, cars) etc:
#   select count of each answer where mode is whatever is selected and append to list
# select count of priority1 = bikes, cars, etc, where mode is selected and append to list
# select count of priority4 = bikes cars, etc where mode is selected and append to list
# final output is nested lists of ints [[ped config answer counts], [bike config answers], [car config answers], [transit config answers]],
#   [hiPri ped counts, hiPri bike count, hiPri car count, hiPri transit count], [another list same as hiPri but loPri]]

#this will become the Pane 1 routing function
#wanted output format: 
# currentlySuitsData = {"car": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25},
# 					"bike": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25,},
# 					"transit": {"stronglyAgree": 4, "agree": 5, "neutral": 9, "disagree": 15, "stronglyDisagree": 25}}
def makePane1(filterValue):

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

filterValue = "%Biking%" # this will be pulled in from filter post request. NOTE THAT WE WILL HAVE TO WRAP OUR FILTER PARAMETER IN THE %S!!
#print(makePane1(filterValue))


#PANE 2: showing random comments 
# What people said (not from same person):
# field: Like
# field: WishDifferent
# one random from fields IdeasCars, IdeasTransit, IdeaseBikes, IdeasPeds
# output is list of strings, ["random Like", "random WishDifferent", "random idea field 
# (so we can label it on the page)", "random idea"]
#psuedocode:
#initialize list to hold strings
#generate random number
#use random number to select a record with that responseID and select Like from that ID's record and add to list
#generate another random number
#use it to select another record and get that ID's WishDifferent string and add to list
#choose ideas field randomly
#generate another random number
#use it to select the contents of the randomly chosen ideas field and add to list along with the field label

# NOTE: other things in Pane 2 will be static, we will need to handpick the data for that

def getRandom(targetField):
    conn = s.connect("../telegraph.db")
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
    textData = []
    textData.append(getRandom("Like"))
    textData.append(getRandom("WishDifferent"))
    randomIdea = random.choice(["IdeasCars", "IdeasTransit", "IdeaseBikes", "IdeasPeds"])
    textData.append(randomIdea)
    textData.append(getRandom(randomIdea))
    return textData
        
    #return statement will hand textData object off to the front end

#print(makePane2())

#PANE 3: survey respondent info
# How often are you on teleGraph
# Where do you live graph
# Primary mode of transit graph
# Connection to telegraph venn diagram
# functions are separate for now (they can be combined later if nec).
# one for each chart

# 3a: frequency
def getFrequency():
     frequency = answerCount(("Daily", "A few times per week", "A few times per month", "Rarely"), "Frequency", "ResponseID", "IS NOT", "None") #those last parameters are just essentially dummies to satisfy the function
     # print(frequency)
     return frequency

# 3b: where do you live
# want: a dict with key/values of place/count
# keys: Oakland, Berkeley, San Francisco, Other East Bay, North Bay, South Bay, Other CA, Other
# join r.HomeZIP to zips.City and select the count of records where zips.City = Oakland

def getLocation():
    location = {}
    conn = s.connect("../telegraph.db")
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

#print(getLocation())

#3c: mode of transit--enter "Mode1" as param for first and "Mode6" for last
# including empty string in the answers for now b/c I feel no response is maybe an illuminating data point for this
# can't use answerCount() for this b/c of the slightly difft structure needed for the SQL statement
def getMode(priority):
    conn = s.connect("../telegraph.db")
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
    
print(getMode("Mode1"))
# print(getMode("Mode6")) 

#3d: venn diagram for connection to telegraph ave
#the output should be structured like so:
# sets = [{label: "A", size: 10}, {label: "B", size: 10}], overlaps = [{sets: [0,1], size: 2}]
# first make the sets

def makeVenn(setParams):
    '''takes list of lists where item[0] are fieldnames for set, item[1] are answers to be included in the set;
    not using a dict for this b/c order of items needs to be totally predictable to generate the overlaps;
    returns a list of lists: list[0] is a list sets where each set is a dict with a label and a size, like so: 
    [{label: "A", size: 10}, {label: "B", size: 10}]; list[1] is a list of overlaps like so: [{sets: [0,1], size: 2}]
    set labels will be added to the items by the list.index() method.'''
    
    conn = s.connect("../telegraph.db")
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
    
    #to make the overlaps
    #can use itertools.combinations() to produce iterators of all the combinations of a given size
    #so call itertools.combinations(setParams, n) for n in range(2, len(setParams) + 1)
    #each item in each itertools.combinations() object makes a database call: select count where item[0][0] = item[0][1] and item[1][0] = item[1][1]
    #but how to get them labelled right? because the venn library needs them labeled with indices of list position in the set list
    # list.index() method!! wheeeee. wait no. this won't work b/c by the time it's in the itertools context it has been detached from
    # its original list position. so that does need to be put into the original setParams. Damn.  
    
    
    for n in range(2, len(setParams) + 1):
        nCombos = itertools.combinations(setParams, n)
        for combo in nCombos:
            overlapEntry = {}
            #after much thinking, doing it one by one is going to be the way to go b/c of the fact that column names can't be parameterized
            #do the database call here so right # of ?s can be inserted into SQL
            #this is frustrating b/c it would be so much more elegant to have a makeSets function and a makeOverlaps function and call them both in makeVenn()
            #and it's clearly possible b/c of the repeating patterns but it would take so much more time to do it that way now that I have a method that works even though it's clunky!!
            #i started off making something extensible and now this is totally not at all. :(
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
    print(len(overlaps))
            
            
      
    cur.close()
    conn.close()    
    return vennData

tgraphConnection = [["Resident", "Yes"], ["Business", "Yes"], ["Work", "Yes"], ["Visit", "Yes"], ["Commute", "Yes"]]
print(makeVenn(tgraphConnection))

#print(getFrequency())
    
    

