import os
import os.path
import sys
import platform


findingsfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/exstra_dictionary_COMPLETE.tsv"
text_file = open(findingsfile, "r", encoding='utf-8')
findingsstr = text_file.read()
text_file.close()
findingstab = []
for row in findingsstr.split("\n"):
    findingstab.append(row.split('\t'))

blacklist = "C:\\Users\\flo-f\\Documents\\GitHub\\ExSTRA\\blacklist.txt"
blacklist_file = open(blacklist, "r", encoding='utf-8')
blackliststr = blacklist_file.read()
text_file.close()
blacklst = []
for element in blackliststr.split("\n"):
    blacklst.append(element)
    
cleantable = []

for r in range(len(findingstab)):
    row = findingstab[r]
    try:
        if row[1] not in blacklst:
            cleantable.append(row)
    except:
        pass
        
newtable = []
for cr in range(len(cleantable)):
    cleanrow = cleantable[cr]
    try: 
        if "nobiliary particle" not in cleanrow[6]:
            newtable.append(cleanrow)
    except:
        pass

print(newtable[:5])

fileName = "clean_COMPLETE.tsv"
separatore = "\t"
stringarisultato = ""
for r in range(len(newtable)):
    for i in range(len(newtable[r])):
        if i > 0:
            stringarisultato = stringarisultato + separatore
        try:
            stringarisultato = stringarisultato + str(newtable[r][i])
        except:
            pass
    stringarisultato = stringarisultato + "\n"
    #Scrivo la stringa in un file di testo CSV
text_file = open(fileName, "w", encoding='utf-8')
text_file.write(stringarisultato)
text_file.close()