# GRAPH 1: Is current config good for <mode of transit>
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
# final output is [[ped config answer counts], [bike config answers], [car config answers], [transit config answers]],
#   [hiPri ped counts, hiPri bike count, hiPri car count, hiPri transit count], [another list same as hiPri but loPri]]

import sqlite3 as s

def answerCount(targetAnswers, targetField, filterField, filterValue):
    '''Takes a tuple of possible answer values in the target field, the name of the target field, 
    the name of the field  that the query filters on, and a value for the query to filter that field on. 
    returns a list of counts for each answer in the target field (in the order the answers
    were supplied in the tuple)'''
    
    returnList = []
    for item in targetAnswers:
        data = (filterValue, item)
        #technically I know it's not "safe" to build SQL queries this way but b/c it's a SELECT and we are supplying the data I think it's ok
        SQL = "SELECT COUNT(" + targetField + ") from r WHERE " + filterField + " LIKE ? AND " + targetField + " = ?;" #gets count of each answer in the target field
        cur.execute(SQL, data)
        returnList.append((cur.fetchone()[0])) #appends count to the list
    return returnList


conn = s.connect("../telegraph.db")
conn.text_factory = str
cur = conn.cursor()

#this will become the graph1 routing function
#probably should put the opening/closing of connection and cursor in that function when we get to that
graphData = []
filterField = "Mode1"
filterValue = "%Biking%" # this will be pulled in from filter post request. NOTE THAT WE WILL HAVE TO WRAP OUR FILTER PARAMETER IN THE %S!!

#for "Does current config work?" question
configAnswers = ("Strongly Agree", "Agree", "No Opinion", "Disagree", "Strongly Disagree", "") 
configTargets = ("GoodPeds", "GoodBikes", "GoodCars", "GoodTransit")
configuration= []
for item in configTargets:
    configuration.append(answerCount(configAnswers, item, filterField, filterValue))
# print(configuration)
graphData.append(configuration)

#for the highest priority improvements chart
priorityAnswers = ("Biking", "Driving", "Transit", "Walking")
hiPri = answerCount(priorityAnswers, "Improve1", filterField, filterValue)
#print(hiPri)
graphData.append(hiPri)
#print(graphData)

#for the lowest priority improvements chart
loPri = answerCount(priorityAnswers, "Improve4", filterField, filterValue)
#print(loPri)
graphData.append(loPri)
#print(graphData)

cur.close()
conn.close()