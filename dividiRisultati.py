import os
import os.path
import sys
import platform

tagDct = {"profession" : "professions.tsv", "nobiliary particle": None, "noble rank": "nobles.tsv", "honorary title": "Q3320743", "ecclesiastical occupation": "professions.tsv", "historical profession": "Q16335296", "military rank": "Q56019", "human": "Q5", "factory (place)": "Q83405", "facility (place)": "Q13226383", "workplace (place)": "Q628858", "shop (place)": "Q213441", "commercial building (place)": "Q655686", "religious building (place)": "Q24398318", "house (place)": "Q3947", "rural building (place)": "Q131596", "fortification (place)": "Q57821", "venue (place)": "Q17350442"}

findingsfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/exstra_dictionary_COMPLETE.tsv"
text_file = open(findingsfile, "r", encoding='utf-8')
findingsstr = text_file.read()
text_file.close()

for k in tagDct:
    if k == None:
        continue
    text_file = open(tagDct[k], "w", encoding='utf-8')
    text_file.write("")
    text_file.close()
    

for line in findingsstr.split("\n"):
    tag = line.split("\t")[6]
    for k in tagDct:
        if k == None:
            continue
        if k in tag:
            filename = tagDct[k]
            break
    with open(filename, "a") as file_object:
        file_object.write(line + "\n")
            
      