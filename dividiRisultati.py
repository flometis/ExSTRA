import os
import os.path
import sys
import platform

tagDct = {"profession" : "professions.tsv", "nobiliary particle": None, "noble rank": "professions.tsv", "honorary title": None, "ecclesiastical occupation": "professions.tsv", "historical profession": "professions.tsv", "military rank": "professions.tsv", "human": None, "factory (place)": "places-industrial.tsv", "facility (place)": None, "workplace (place)": None, "shop (place)": "places-commercial.tsv", "commercial building (place)": "places-commercial.tsv", "house (place)": "places-civil.tsv", "rural building (place)": "places-rural.tsv", "fortification (place)": "places-military.tsv", "venue (place)": None, "religious building (place)": "places-religious.tsv", "industrial (place)": "places-industrial.tsv", "commercial building (place)": "places-commercial.tsv", "civil building (place)" : "places-civil.tsv", "public (place)": "places-public.tsv"}

findingsfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/exstra_dictionary_COMPLETE.tsv"
text_file = open(findingsfile, "r", encoding='utf-8')
findingsstr = text_file.read()
text_file.close()

blacklist = "C:\\Users\\flo-f\\Documents\\GitHub\\ExSTRA\\blacklist.txt"
blacklist_file = open(blacklist, "r", encoding='utf-8')
blackliststr = blacklist_file.read()
text_file.close()
blacklst = []
for element in blackliststr.split("\n"):
    blacklst.append(element)

for k in tagDct:
    if tagDct[k] == None:
        continue
    text_file = open(tagDct[k], "w", encoding='utf-8')
    text_file.write("")
    text_file.close()
text_file = open("places.tsv", "w", encoding='utf-8')
text_file.write("")
text_file.close()

for line in findingsstr.split("\n"):
    try:
        tag = line.split("\t")[6]
    except:
        continue
    filename = None
    if line.split("\t")[1] in blacklst:
        continue
    for k in tagDct:
        if tagDct[k] == None:
            continue
        if k == tag:
            filename = tagDct[k]
            break
    try:
        with open(filename, "a", encoding="utf8") as file_object:
            file_object.write(line + "\n")
        if filename != "professions.tsv":
            with open("places.tsv", "a", encoding="utf8") as file_object:
                file_object.write(line + "\n")
    except:
        pass
             