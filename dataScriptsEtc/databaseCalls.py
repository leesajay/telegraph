#PSEUDOCODE FOR DATABASE CALLS

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
# for each of peds, cars, etc:
#   select count of each answer where mode is whatever is selected and append to list
# select count of priority1 = bikes, cars, etc, where mode is selected and append to list
# select count of priority4 = bikes cars, etc where mode is selected and append to list
# final output is [[ped config answer counts], [bike config answers], [car config answers], [transit config answers]],
#   [[hiPri ped counts], [hiPri bikes], [hiPri cars], [hiPri transit]], [another list of lists same as hiPri but loPri]]

import sqlite3 as s

conn = s.connect("../telegraph.db")
conn.text_factory = str
cur = conn.cursor()

# #test connection
# cur.execute("SELECT * FROM r WHERE ResponseID = '1';")
# print(cur.fetchone())

#graph1
#sample will be for respondents who use a bike as a primary transit mode
mode = "%Biking%" #NOTE THAT WE WILL HAVE TO WRAP OUR FILTER PARAMETER IN THE %S!!
finalObj = [] #not gonna use this yet, just building the configuration list first
configuration = []
pedsCon = []
bikesCon = []
carsCon =[]
transCon = []


#Molly--eventually I think it would make sense to make this a function, so that answerCount(GoodPeds, mode)
# would return the appropriate list and then that would get added to the config file. I can write another one
# for the priority lists. So then our routing functions will just be calling the necessary answerCount functions with the 
#parameters from the filter and the container. Not sure I am explaining it right...
answers = ("Strongly Agree", "Agree", "No Opinion", "Disagree", "Strongly Disagree", "")
for item in answers:
    data = (mode, item)
    SQL = "SELECT COUNT(GoodPeds) from r WHERE Mode1 LIKE ? AND GoodPeds = ?;" #gets count of each answer for peds
    cur.execute(SQL, data)
    pedsCon.append((cur.fetchone()[0])) #appends count to the list

#pedsCon is verified as a list of ints that gets appended to configuration
configuraton.append(pedsCon)

cur.close()
conn.close()