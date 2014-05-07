import sqlite3 as s
import itertools

#output i need here is to like the other bar charts:
#{"column label": count, "column label": count}

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
                
    #need to get count of people only in one category
#     #SQL = "SELECT COUNT(ResponseID) FROM r WHERE " + columnName + " = 'Yes' AND " + other columns + " = 'No'"
#     residentOnlySQL = '''SELECT COUNT(ResponseID) FROM r WHERE Resident = "Yes" 
#     AND Business != "Yes" AND Work != "Yes" AND Visit != "Yes" AND Commute != "Yes";'''
#     cur.execute(residentOnlySQL)
#     residentOnlyCount = cur.fetchone()[0]
#     print(residentOnlyCount)
#     
#     businessOnlySQL = '''SELECT COUNT(ResponseID) FROM r WHERE Business = "Yes" 
#     AND Resident != "Yes" AND Work != "Yes" AND Visit != "Yes" AND Commute != "Yes";'''
#     cur.execute(businessOnlySQL)
#     businessOnlyCount = cur.fetchone()[0]
#     print(businessOnlyCount)
#     
#     workOnlySQL = '''SELECT COUNT(ResponseID) FROM r WHERE Work = "Yes" 
#     AND Business != "Yes" AND Resident != "Yes" AND Visit != "Yes" AND Commute != "Yes";'''
#     cur.execute(workOnlySQL)
#     workOnlyCount = cur.fetchone()[0]
#     print(workOnlyCount)
#     
#     visitOnlySQL = '''SELECT COUNT(ResponseID) FROM r WHERE Visit = "Yes" 
#     AND Business != "Yes" AND Resident != "Yes" AND Work != "Yes" AND Commute != "Yes";'''
#     cur.execute(visitOnlySQL)
#     visitOnlyCount = cur.fetchone()[0]
#     print(visitOnlyCount)
#     
#     commuteOnlySQL = '''SELECT COUNT(ResponseID) FROM r WHERE Commute = "Yes" 
#     AND Business != "Yes" AND Resident != "Yes" AND Visit != "Yes" AND Work != "Yes";'''
#     cur.execute(workOnlySQL)
#     commuteOnlyCount = cur.fetchone()[0]
#     print(commuteOnlyCount)
    
    #for two connections only:
    
    
    vennReplacement = [{"One connection only": residentOnlyCount+businessOnlyCount+workOnlyCount+visitOnlyCount+commuteOnlyCount}]
                
                
                
    vennData.append(overlaps)
                        
    cur.close()
    conn.close()    
    return vennData

tgraphConnection = [["Resident", "Yes"], ["Business", "Yes"], ["Work", "Yes"], ["Visit", "Yes"], ["Commute", "Yes"]]
vennData = (makeVenn(tgraphConnection))