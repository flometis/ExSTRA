import urllib.request
import urllib.parse
import re
import html
import sys
import os
import json
import datetime
import time
from socket import timeout

#List of the Wikidata entities we can download. If you need another one, just add it to the dictionary
entities = { "profession" : "Q28640", "nobiliary particle": "Q355505", "noble rank": "Q355567", "honorary title": "Q3320743", "ecclesiastical occupation": "Q11773926", "historical profession": "Q16335296", "military rank": "Q56019", "human": "Q5"}

#Any language can be used, I'm laying these out just as examples
langs = {"inglese":"en", "italiano":"it", "tedesco":"de", "francese":"fr", "siciliano":"scn", "lombardo": "lmo", "friulano": "fur", "emiliano romagnolo":"eml", "romagnolo": "rgn", "veneto":"vec", "croato":"hr", "sloveno":"sl", "corso": "co", "etrusco":"ett", "franco provenzale": "frp", "latino": "la", "ladino": "lld", "napoletano": "nap", "occitano": "oc", "ligure": "lij", "monegasco": "lij-mc", "greco antico": "grc", "piemontese": "pms", "tarantino": "roa-tara", "sardo": "sc", "sassarese": "sdc", "albanese": "sq", "spagnolo": "es", "portoghese": "pt"}          
#Full list of supported languages: https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all

#Config for the web downloader
useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
#useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
mytimeout = 60

#URLs to get data from
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
SAPERE_URL = "https://www.sapere.it/sapere/enciclopedia/storia-e-societ%C3%A0/economia-e-statistica/generale/mestieri-e-professioni.html?src="

language = ""

# This function gets the content of a web page safely. If you're looking for wikidata specific functions, skip this
def geturl(thisurl, params = None):
    global useragent
    global mytimeout
    #Just a safety check, do not run if thisurl is empty
    if thisurl == '':
        return ''
    #params should be a dictionary with the arguments required by the webpage (eg: wikidata entity to retrieve)
    if params == None:
        #in case we don't have any parameter, then data should be none
        mydata = None
    else:
        #if we got parameters, turn em into a array of bytes (ascii) instead of a string (utf-8)
        mydata = urllib.parse.urlencode(params)
        mydata = mydata.encode('ascii')
    #this is the actual HTTP request, we're just building it, not sending
    req = urllib.request.Request(
        thisurl,
        data=mydata,
        headers={
            'User-Agent': useragent
        }
    )
    
    #thishtml will be the content of the webpage retrieved
    thishtml = ""
    #Now we're sending the HTTP request, reading the webpage as a bytes array
    try:
        f = urllib.request.urlopen(req,timeout=mytimeout)
        ft = f.read() #we should stop if this is taking too long
    except:
        ft = ""
        print("Error sending request to "+thisurl)
    #We need to get the bytes array into a string. But we first need to discover the encoding
    try:
        encoding = f.info().get_content_charset() #f.headers.get_content_charset()
        if encoding == None:
            encoding = 'windows-1252'
        thishtml = ft.decode(encoding)
        #print(encoding)
    except:
        try:
           thishtml = ft.decode('utf-8', 'backslashreplace')
        except:
           thishtml = str(ft)
    #Now we should have the webpage as a string. We just need to remove HTML escape sequences, things like &quote;. And we use html.unescape function
    try:
        thishtml = html.unescape(thishtml)
    except Exception as e:
        print(e)
        #thishtml = ""
    return thishtml


#This is a simple function to merge tables obtained by multiple iterations
def mergeTables(table1, table2):
    #TODO: check if table1 structure (number of columns) matches table2
    table1.extend(table2)
    return table1

def mergeResultTables(table1, table2):
    mytable = table1
    mytable.extend(table2)
    mytable = sorted(mytable)
    #columns:
    #ID,lemma,source,language,tag,descrizione
    mytbclean = [mytable[i] for i in range(len(mytable)) if i == 0 or mytable[i][:-1] != mytable[i-1][:-1]]   #the last element is the description
    #mytbclean = []
    #for i in range(len(mytable)):
    #    if i == 0 or bool(mytable[i][0] != mytable[i-1][0] and mytable[i][1] != mytable[i-1][1]):   #the last element is the description
    #        mytbclean.append(mytable[i])
    #    else:
    #        if mytable[i][4] not in mytbclean[-1][4]: #4 is the category
    #            mytbclean[-1][4] = mytbclean[-1][4] + ";" + mytable[i][4]
    return mytbclean


def sortTable(table, sortColumn = 0):
    res = table
    try:
        res.sort(key=lambda x: x[sortColumn])  #sort by specified column
    except:
        try:
            res.sort(key=lambda x: x[0])  #Fallback: sort by column 0
        except:
            res = table #Last resort: do not sort
    return res

def groupTable(mytable, id=0):
    table = mytable
    history = dict()
    for r in range(len(table)):
        if table[r][id] in history:
            oldR = history[table[r][id]]
            for c in range(len(table[r])):
                try:
                    if table[r][c] not in table[oldR][c].split("|"):
                        table[oldR][c] = table[oldR][c] + "|" + table[r][c]
                except:
                    pass
            table[r] = []
        else:
            history[table[r][id]] = r
    for r in range(len(table)-1, -1, -1):   #go from total number of rows to 0, stepping down (step is -1, not +1). 
        if len(table[r]) == 0:
            del table[r]
    return table




#TODO: Maybe insert column names as first row, skip first row when merging tables (if first row of two tables is equal you can merge, but skip first row of the table that needs to be added at the end of the other one). But maybe it's not that useful, we'll see in the future


#Notes for query optimization: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/query_optimization#Label_service
#This function get instances of some entity from  wikidata
def getInstanceOf(entity, language = "en", year = "NaN", sort = True):
    global entities
    print("Looking for " + str(entity) + " in language " + str(language) + ", year " + str(year) + "")
    #First of all, we need to write down the query for wikidata
    if entities[entity]=="Q5":   #If the entity we're looking for is humans (code Q5), things are a little more complex
        if year < 0:
            addyears = 2
        else:
            addyears = 1
        query_string = "SELECT ?item ?itemLabel ?occupationLabel ?genderLabel ?citizenshipLabel ?birth \n"
        query_string = query_string + "WITH {\n"
        query_string = query_string + "SELECT ?item ?gender ?occupation ?citizenship ?birth WHERE { \n"  
        query_string = query_string + "?item wdt:P31 wd:"+entities[entity]+";\n" #P31 means we are looking for items that are instances of the entity
        query_string = query_string + "        wdt:P21 ?gender;\n"
        query_string = query_string + "        wdt:P106 ?occupation;\n"
        query_string = query_string + "        wdt:P27 ?citizenship;\n"
        query_string = query_string + "        wdt:P569 ?birth.  hint:Prior hint:rangeSafe true.\n"
        try:
            query_string = query_string + "filter (?birth > \""+str(year)+"-00-00\"^^xsd:dateTime && ?birth < \""+str(int(year)+addyears)+"-00-00\"^^xsd:dateTime)\n"
        except:
            return
        query_string = query_string + "}\n"
        query_string = query_string + "} AS %results \n"
        query_string = query_string + "WHERE {\n"
        query_string = query_string + "INCLUDE %results.\n"
        query_string = query_string + "?item rdfs:label ?itemLabel. FILTER( LANG(?itemLabel)=\""+language+"\" )\n"
        query_string = query_string + "?gender rdfs:label ?genderLabel. FILTER( LANG(?genderLabel)=\"en\" )\n"
        query_string = query_string + "?occupation rdfs:label ?occupationLabel. FILTER( LANG(?occupationLabel)=\"en\" )\n"
        query_string = query_string + "?citizenship rdfs:label ?citizenshipLabel. FILTER( LANG(?citizenshipLabel)=\"en\" )\n"
        query_string = query_string + "}\n"
    else:
        #if looking for a generic entity (not humans), the qeury is quite simple
        query_string = "\nSELECT ?item ?itemLabel ?itemDescription WHERE {\n"
        query_string = query_string + "SERVICE wikibase:label { bd:serviceParam wikibase:language \""+language+"\". }\n"
        query_string = query_string + "?item wdt:P31 wd:" + entities[entity] + ".\n"   
        query_string = query_string + "}\n"
        
    #The parameters needed by geturl function are stored into a dictionary
    myparams={"query": query_string, "format": "json"}
    #Send the HTTP request and read the output
    resultsStr = geturl(WIKIDATA_SPARQL_URL, myparams)
    #the output is a json text, we turn it into an object (nested dictionaries and lists)
    results = json.loads(resultsStr)
    
    #print(json.dumps(results["results"]["bindings"][1]))  #decomment for debug

    #build table as many columns as are the properties of the entity
    resultsTable = []
    for res in results["results"]["bindings"]:
        #Sample of res dictionary:
        #{"item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q76237"}, "itemLabel": {"xml:lang": "en", "type": "literal", "value": "Georg Friedrich Kolb"}, "genderLabel": {"xml:lang": "en", "type": "literal", "value": "male"}, "occupationLabel": {"xml:lang": "en", "type": "literal", "value": "journalist"}}
        try:
            if bool(res["itemLabel"]["xml:lang"]!=language) or re.match(".*[0-9].*", res["itemLabel"]["value"]):
                continue  #If the item does not have a label in the language we're looking for, just skip it
        except:
            continue
        myrow = []
        for key in res:
            #first key:value is the ID, then we get lemma and description
            if len(myrow)==1:
                myrow.append(res[key]["value"].lower())
                myrow.append("wikidata")
                myrow.append(language)
                myrow.append(entity)
            else:
                myrow.append(res[key]["value"])
        if len(res) < 3:
            myrow.append("") #empty description
        resultsTable.append(myrow)
    
    #If you want sorted results, do it
    if sort:
        resultsTable = groupTable(resultsTable, 0)
        resultsTable = sortTable(resultsTable, 1)
    return resultsTable

def getSapereProfessions():
    #Note: some letters are not available in the website
    ALPHABET = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "L", "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "X", "Z"] #http://www.sapere.it/sapere/enciclopedia/storia-e-societ%C3%A0/economia-e-statistica/generale/mestieri-e-professioni.html?src=A
    
    resultsTable = []
    #we look for boundaries of the text inside the webpage
    start = "all_lemmas"
    end = "</ul>"
    #we read every page of the website
    for letter in ALPHABET:
        myhtml = geturl(SAPERE_URL+letter.lower())
        #use slicing to extract only the text block, skipping CSS and JS lines
        startpos = myhtml.find(start)
        endpos = myhtml.rfind(start)
        endpos = myhtml.find(end, endpos)
        myhtml = myhtml[startpos:endpos]
        #every word is wrapped inside title=""
        regex = ".*?title=[\"'](.*?)[\"']"
        words = [m.group(1) for m in re.finditer(regex, myhtml, flags=re.DOTALL)]
        #every webpage URL with a word description is wrapped inside href=""
        regex = ".*?href=[\"'](.*?)[\"']"
        links = [m.group(1) for m in re.finditer(regex, myhtml, flags=re.DOTALL)]
        print(SAPERE_URL+letter.lower())
        for i in range(len(links)):
            #we look at every page for every word, getting its description
            thisurl = "http://www.sapere.it"+links[i]
            wordhtml = geturl(thisurl)
            #luckily, the description of the word is written inside a <meta description/> tag
            regex = ".*?<meta content=\"(.*?)\" name=\"description\"\/>.*?"
            m = re.match(regex, wordhtml, flags=re.DOTALL)
            definition = m.group(1)
            #now we've got the word, its full url, and its description: we add them to the table in a new row
            resultsTable.append([thisurl, words[i], "sapere", "it", definition])
        print(resultsTable[-1]) #we print the last row of the table, just to let the user know what it the last word read. It's a long process, it's good to know if it's still running
    return resultsTable
    
def saveTable(table, outFile):
    #write empty file
    text_file = open(outFile, "w", encoding='utf-8')
    text_file.write("")
    text_file.close()
    #now write one line after the other
    for row in table:
        #we need to build the new line for the file: it's going to be the list of cells in current table row, separated by tab
        rowtxt = ""
        for col in row:
            rowtxt = rowtxt + "\t" + col.replace(',',';')
        try:
            #mode "a" means append to file
            with open(outFile, "a", encoding='utf-8') as myfile:
                myfile.write(rowtxt[1:]+"\n")
        except:
            #maybe Windows is just slow. Take a nap for 0.05 seconds (50 milliseconds) and try again
            time.sleep(0.05)
            #mode "a" means append to file
            with open(outFile, "a", encoding='utf-8') as myfile:
                myfile.write(rowtxt[1:]+"\n")
            

def openTable(inFile, sep = "\t"):
    text_file = open(inFile, "r", encoding='utf-8')
    patternlist = text_file.read()
    text_file.close()
    mytable = []
    for row in patternlist.split("\n"):
        if row=="":
            continue
        mytable.append(row.split(sep))
    return mytable

def cleanAccents(parola):
    pulita = parola.replace("à", "a")
    pulita = pulita.replace("è", "e")
    pulita = pulita.replace("é", "e")
    pulita = pulita.replace("ì", "i")
    pulita = pulita.replace("ò", "o")
    pulita = pulita.replace("ó", "o") 
    pulita = pulita.replace("ù", "u")  
    pulita = re.sub("[^a-z]", "", pulita.lower())
    return pulita

def mergeSapere(mytable):
    sapere = openTable("listing_sapere_profession_it.tsv")
    transTable = list(map(list, zip(*mytable)))
    #transTable = list(map(list, itertools.zip_longest(*mytable, fillvalue="")))
    for r in range(len(sapere)):
        if cleanAccents(sapere[r][1]) not in transTable[1]:
            newrow = [sapere[r][0],cleanAccents(sapere[r][1])]
            newrow.extend(sapere[r][2:])
            mytable.append(newrow)
    return mytable
    
#Main routine:
source = "1"
#print("Available sources:\n 1 - Wikidata\n 2 - Sapere.it")
#source = input("Where do you want to get data from?")
#if source == "2":
#    mytable = getSapereProfessions()
#    myentity = "sapere_profession"
#    mylang = "it"
#    filename = os.path.abspath(os.path.dirname(sys.argv[0])) + "/listing_"+ myentity + "_" + mylang +".tsv"    
#    saveTable(mytable, filename)
#    print("Saved in " + filename)
#    sys.exit()

print("Command line arguments: python3 extract_dictionary.py entitiesList languagesList [yearFrom] [yearTo]")
print("E.g.: python3 extract-dictionary.py all it,scn,eml,ven")
print("E.g.: python3 extract-dictionary.py human it 1800 1801")

if len(sys.argv)>1:
    if sys.argv[1] == "help":
        sys.exit()

print("\nSupported entites:")
for key in entities:
    print("'" + key + "'")
print("Press Ctrl+C to exit")
myentity = "none"
try:
    myentity = sys.argv[1]
except:
    while bool(myentity not in entities and myentity.lower() != "all" and "," not in myentity):
        myentity = input("Which entity do you want to list? (Write 'all' to get everything except humans search) ")

myentityList = []
if myentity == "all":
    for key in entities:
        if key == "human":
            continue
        myentityList.append(key)
elif "," in myentity:
    myentityList = myentity.split(",")
else:
    myentityList = [myentity]
myentity = ""

print("Example of languages (choose 'all' for all supported languages or use ',' as separator):")
for key in langs:
    print(langs[key] + " (" + key + ")")
print("Full languages list: https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all")
try:
    tmplang = sys.argv[2]
except:
    tmplang = input("Which language do you want?")


filename = os.path.abspath(os.path.dirname(sys.argv[0])) + "/exstra_dictionary.tsv"

if tmplang == "all":
    mylangs = []
    for key in langs:
        mylangs.append(langs[key])
elif "," in tmplang:
    mylangs = tmplang.split(",")
else:
    mylangs = [tmplang]

for mylang in mylangs:
    #if we are looking for humans (Q5) probably we need to run the query many times (one run for every year of birth we need). This means we'll need to merge tables, so we also sort only at the end. Sorting every table before merging it would be a waste of time, we do it only once, after all table are merged into a single one
    if "human" in myentityList:
        try:
            yearfrom = sys.argv[3]
            yearto = sys.argv[4]
        except:
            yearfrom = input("From which year do you want to start? (years BC are < 0)")
            yearto = input("To which year do you want to stop?")
        mytable = []
        for year in range(int(yearfrom), int(yearto)):
            tmptable = getInstanceOf("human", mylang, year, sort=False)
            mergeTables(mytable, tmptable)
            #time.sleep(10)
        mytable = groupTable(mytable, 0)
        mytable = sortTable(mytable, 2) 
    else:
        mytable = []
        for myentity in myentityList:
            mytable.extend(getInstanceOf(myentity, mylang))

    #It's safer to specify full path of the file. We could ask the user for it, but that's for the future
    #filename = os.path.abspath(os.path.dirname(sys.argv[0])) + "/listing_"+ myentity + "_" + mylang +".tsv"
    try:
        oldtable = openTable(filename)
    except:
        oldtable = []
    print("Merging "+str(len(mytable))+" with "+str(len(oldtable))+" previous results...")
    fulltable = mergeResultTables(mytable, oldtable)
    saveTable(fulltable, filename)
    print("Saved in " + filename)
if "it" in mylangs and "exstra_dictionary" in filename:
    fulltable = openTable(filename)
    fulltable = mergeSapere(fulltable)
    saveTable(fulltable, filename)

