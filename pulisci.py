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
    {"find": "\r", "rep": "\n", "flag": 0, "tag": "carriageReturn"},
    {"find": "\n[\n]+", "rep": "\n", "flag": 0, "tag": "inviiMultipli"},
    {"find": "^\s*", "rep": "", "flag": re.MULTILINE, "tag": "spazioInizioRiga"},
    {"find": "([^\s])\-\s*\n", "rep": "\g<1>", "flag": 0, "tag": "paroleSpezzate"},
    {"find": "\s*\#+.*\#+\s*", "rep": "", "flag": re.MULTILINE, "tag": "numeroPaginaCancelletto"},
    {"find": "([^\.\!\?\n\s])\s*\n", "rep": "\g<1>", "flag": 0, "tag": "invioAMetaFrase"},
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
        print('\r'+str(int((i/len(toDo))*100)) + "%", end='', flush=True)
        fulltext = re.sub(operazione["find"], operazione["rep"],  fulltext, flags=operazione["flag"])
    print("\n") 
    
    output = os.path.abspath(os.path.dirname(sys.argv[0])) + "/Eltec100/puliti/" + os.path.basename(filename)
    so = platform.system()
    if so == "Windows":
        output = output.replace("/", "\\")
    text_file = open(output, "w", encoding='utf-8')
    text_file.write(fulltext)
    text_file.close()
    
