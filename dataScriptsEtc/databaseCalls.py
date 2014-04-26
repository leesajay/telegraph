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

import sqlite3 as s
import random

def answerCount(targetAnswers, targetField, filterField, operator, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a list of counts for each answer in the target field (in the order the answers
    were supplied in the tuple)'''
    
    conn = s.connect("../telegraph.db")
    conn.text_factory = str
    cur = conn.cursor()

    returnList = []
    for item in targetAnswers:
        data = (filterValue, item)
        #technically I know it's not "safe" to build SQL queries this way but b/c it's a SELECT and we are supplying the data I think it's ok
        SQL = "SELECT COUNT(" + targetField + ") from r WHERE " + filterField + " " + operator + " ? AND " + targetField + " = ?;" #gets count of each answer in the target field
        cur.execute(SQL, data)
        returnList.append((cur.fetchone()[0])) #appends count to the list
    
    cur.close()
    conn.close()

    return returnList


#this will become the Pane 1 routing function
def makePane1():

    graphData = []
    filterField = "Mode1"
    filterValue = "%Biking%" # this will be pulled in from filter post request. NOTE THAT WE WILL HAVE TO WRAP OUR FILTER PARAMETER IN THE %S!!
    operator = "LIKE"
    #for "Does current config work?" question
    configAnswers = ("Strongly Agree", "Agree", "No Opinion", "Disagree", "Strongly Disagree", "") 
    configTargets = ("GoodPeds", "GoodBikes", "GoodCars", "GoodTransit")
    configuration= []
    for item in configTargets:
        configuration.append(answerCount(configAnswers, item, filterField, operator, filterValue))
#     print(configuration)
    graphData.append(configuration)

    #for the highest priority improvements chart
    priorityAnswers = ("Biking", "Driving", "Transit", "Walking")
    hiPri = answerCount(priorityAnswers, "Improve1", filterField, operator, filterValue)
    #print(hiPri)
    graphData.append(hiPri)
    #print(graphData)

    #for the lowest priority improvements chart
    loPri = answerCount(priorityAnswers, "Improve4", filterField, operator, filterValue)
    #print(loPri)
    graphData.append(loPri)
    #print(graphData)
    
    return graphData #this needs to be edited to hand off to front end properly

# print(makePane1())

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
# output (for now) is four objects (they can be combined later if nec).
# one for each chart
# the venn diagram should be structured like so:
# var sets = [{label: "A", size: 10}, {label: "B", size: 10}], overlaps = [{sets: [0,1], size: 2}];

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
    cities = ["Oakland", "Berkeley"]
    for city in cities:
        SQL = 'SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip WHERE zips.City = ?;'
        data = (city,)    
        cur.execute(SQL, data)
        location[city] = cur.fetchone()[0]
    
    #gets count for these counties EXCLUDING the cities already counted 
    counties = ["Marin", "San Mateo", "Santa Clara", "Alameda", "Contra Costa", "San Francisco"]
    for county in counties:
        SQL = '''SELECT COUNT(ResponseID) from r LEFT JOIN zips on r.HomeZIP = zips.Zip 
        WHERE zips.County = ? AND zips.City NOT IN ("Oakland", "Berkeley");'''
        data = (county,)
        cur.execute(SQL, data)
        location[county] = cur.fetchone()[0]
        if location[county] == 0:
            del location[county]
    
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
    
    mode = []
    modes = ("%ACT%", "%BART%", "%Biking%", "%Driving%", "%Walking%", "%Other%", "")
    for item in modes:
        SQL = "SELECT COUNT(" + priority + ") from r WHERE " + priority + " LIKE ?;"
        data = (item,)
        cur.execute(SQL, data)
        mode.append(cur.fetchone()[0])
        
    cur.close()
    conn.close()
    
    #add BART and ACT counts together to make one transit count
    ACT = mode.pop(0)
    #ACT is now gone so BART is mode[0]
    BART = mode[0]
    #replace BART with sum of both
    mode[0] = ACT + BART

    return mode
    #NOTE THAT THE ORDER OF THE LIST RETURNED: transit, bike, drive, walk, other
    
# print(getMode("Mode1"))
# print(getMode("Mode6")) 
   
    