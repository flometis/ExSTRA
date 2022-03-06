import os
import os.path
import sys
import platform

tagDct = {"profession" : "professions.tsv", "nobiliary particle": None, "noble rank": "nobles.tsv", "honorary title": None, "ecclesiastical occupation": "professions.tsv", "historical profession": "professions.tsv", "military rank": "professions.tsv", "human": None, "factory (place)": "places-industrial.tsv", "facility (place)": "Q13226383", "workplace (place)": "Q628858", "shop (place)": "places-commercial.tsv", "commercial building (place)": "places-commercial.tsv", "house (place)": "places-civil.tsv", "rural building (place)": "places-rural.tsv", "fortification (place)": "places-military.tsv", "venue (place)": "Q17350442", "religious building (place)": "places-religious.tsv", "industrial (place)": "places-industrial.tsv", "commercial building (place)": "places_commercial.tsv", "civil building (place)" : "places-civil.tsv", "public (place)": "places-public.tsv"}

findingsfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/exstra_dictionary_COMPLETE.tsv"
text_file = open(findingsfile, "r", encoding='utf-8')
findingsstr = text_file.read()
text_file.close()

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
    for k in tagDct:
        if tagDct[k] == None:
            continue
        if k == tag:
            filename = tagDct[k]
            break
    try:
        with open(filename, "a") as file_object:
            file_object.write(line + "\n")
        if filename != "professions.tsv":
            with open("places.tsv", "a") as file_object:
                file_object.write(line + "\n") 
    except:
        pass
             