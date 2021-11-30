import re
import os
import os.path
import sys
import platform

path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Eltec100/Eltec100"

so = platform.system()
if so == "Windows":
    path = path.replace("/", "\\")

filenames = [os.path.abspath(path + "/" + filename) for filename in os.listdir(path)]

toDo = [
    {"find": "[\r\n]+", "rep": "\n", "flag": "", "tag": ""}, 
    {"find": "([^\.\!\?]) *\n", "rep": "\g<1>", "flag": "", "tag": ""},
    ]

for filename in filenames:
    so = platform.system()
    if so == "Windows":
        filename = filename.replace("/", "\\")
    text_file = open(filename, "r", encoding='utf-8')
    fulltext = text_file.read()
    text_file.close()
    print("Sto lavorando su: " + filename)
    
    i = 0
    print("0%", end='')
    for operazione in toDo:
        i = i + 1
        print('\r'+str((i/len(toDo))*100) + "%", end='', flush=True)
        fulltext = re.sub(operazione["find"], operazione["rep"],  fulltext)
    print("\n") 
    
    output = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Eltec100/puliti/" + os.path.basename(filename)
    so = platform.system()
    if so == "Windows":
        output = output.replace("/", "\\")
    text_file = open(output, "w", encoding='utf-8')
    text_file.write(fulltext)
    text_file.close()
    
