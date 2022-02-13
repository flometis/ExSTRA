#!/usr/bin/bash

import subprocess
import os.path
import sys
import time
import os
import platform
import re
import psutil

path = "Eltec100/puliti"
filenames = [filename for filename in os.listdir(path)]

filepath = "Eltec100/Eltec-metadata.tsv"
text_file = open(filepath, "r", encoding='utf-8')
text = text_file.read()
text_file.close()

forceTag = False
if sys.argv[-1] == "--force":
    forceTag = True

so = platform.system()
if  so == "Windows":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-Win64/udpipe"
elif so == "Linux":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-linux64/udpipe"
elif so == "Mac":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-osx/udpipe"
        #È chiaro che su Windows dovresti modificare il nome della cartella in bin-win64
modello = os.path.abspath(os.path.dirname(sys.argv[0])) + "/modelli/italial-all.udpipe"

dct = {"sindex" : 0, "tkn" : 1, "lemma" : 2, "POS" : 3, "RPOS" : 4, "morph" : 5 , "depA": 6, "depB": 7}

ignoretext = "((?<=[^0-9])"+ re.escape(".")+ "|^" + re.escape(".")+ "|(?<= )"+ re.escape("-")+ "|^"+re.escape("-")+ "|"+re.escape(":")+"|(?<=[^0-9])"+re.escape(",")+"|^"+re.escape(",")+"|"+re.escape(";")+"|"+re.escape("?")+"|"+re.escape("!")+"|"+re.escape("«")+"|"+re.escape("»")+"|"+re.escape("\"")+"|"+re.escape("(")+"|"+re.escape(")")+"|^"+re.escape("'")+ "|" + re.escape("[PUNCT]") + "|" + re.escape("[SYMBOL]") + "|" + re.escape("<unknown>") + ")"


tokenRanges = {
"sotto10mila": [0,10000], 
"10_50mila": [10000,50000],
"50_100mila": [50000,100000],
"oltre100mila": [100000, sys.maxsize]
}


def UDtagger(origcorpus):
    global eseguibile
    global modello
    waitUD = True
    while waitUD:
        for proc in psutil.process_iter():
            try:
                if "udpipe" in proc.name().lower():
                    print("Waiting for previous udpipe to end")
                    pass
                else:
                    waitUD = False
                    #print("Good, no other udpipe running")
                    break
            except:
                pass
        time.sleep(1)
    #Udpipe andrebbe lanciato con un comando del tipo ./bin-linux64/udpipe --tokenize --tag --parse ./modelli/italian-isdt-ud-2.4-190531.udpipe
    #Per poterlo avviare da Python con la libreria Subprocess dobbiamo dividere i vari argomenti in elementi di una lista, così non ci sono spazi
    process = subprocess.Popen([eseguibile, "--tokenize", "--tag", "--parse", modello], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    #Per lavorare sullo standard input bisogna usare una sequenza di byte invece di una comune stringa di testo, perché siamo a basso livello. Una stringa può essere codificata come byte usando la sua funzione encode
    testobyte = origcorpus.encode(encoding='utf-8')
    #Una volta si usava questo metodo per scrivere su stdin:
    #process.stdin.write(testo)
    #ma ci sono dei problemi con i testi lunghi. Adesso si usa direttamente la funzione communicate, che allo stesso tempo fornisce anche la risposta elaborata dall'eseguibile
    outputbyte = process.communicate(testobyte)[0]
    #È una buona idea chiudere il flusso dello stdin quando hai finito di scrivere
    process.stdin.close()
    #Chiaramente anche l'output è una sequenza di byte, basta decodificarli in una stringa con la stessa codifica utf-8 usata per l'inpu
    stroutput = outputbyte.decode(encoding='utf-8')
    #print(stroutput)
    return stroutput

def savetable(risultato, fileName = "risultato.tsv", separatore = "\t", header = ""):
    stringarisultato = header
    for r in range(len(risultato)):
        for i in range(len(risultato[r])):
            if i > 0:
                stringarisultato = stringarisultato + separatore
            stringarisultato = stringarisultato + str(risultato[r][i])
        stringarisultato = stringarisultato + "\n"
    #Scrivo la stringa in un file di testo CSV
    text_file = open(fileName, "w", encoding='utf-8')
    text_file.write(stringarisultato)
    text_file.close()


#Main
newtable = []
for r in range(0,len(text.split('\n'))):
    row = text.split('\n')[r]
    line = row.split('\t')
    if r == 0:
        newtable.append(line)
        continue
    if r > 0:
        line[0] = line[0].replace(".xml","")
        line[0] = re.sub('[^a-z]' , '',line[0].lower())
    found = False
    for file in filenames:
        fileclean = re.sub('[^a-z]' , '',file.lower())
        if fileclean.startswith(line[0]):
            found = True
            line[0] = file
    if not found:
        print("ERROR: File "+ line[0] + " not found")
    #Conteggio tokens
    try:
        tnum = int(line[6])
    except:
        tnum = 0
    try:
        if len(line)<2:
            ops = 0/0
        totaltokens = 0
        try:
            text_file = open(path+"/"+line[0], "r", encoding='utf-8')
            corpusraw = text_file.read()
            text_file.close()
        except:
            try:
                text_file = open(path+"/"+line[0], "r", encoding='ISO-8859-15')
                corpusraw = text_file.read()
                text_file.close()
                text_file = open(path+"/"+line[0], "w", encoding='utf-8')
                text_file.write(corpusraw)
                text_file.close()
            except:
                #print("Error reading file")
                pass

        taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(path+"/"+line[0])[:-4]+"-bran.tsv"
        if not os.path.isdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"):
            os.mkdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/")
        so = platform.system()
        if so == "Windows":
            taggedname = taggedname.replace("/", "\\")
        if forceTag or not os.path.isfile(taggedname):
            corpusfile = UDtagger(corpusraw)
        else:
            print("Tagged corpus "+taggedname+" already exists, not tagging again.")
            text_file = open(taggedname, "r", encoding='utf-8')
            corpusfile = text_file.read()
            text_file.close()
        text_file = open(taggedname, "w", encoding='utf-8')
        text_file.write(corpusfile)
        text_file.close()

        corpuslist = corpusfile.split("\n")
        totaltokens = len(corpuslist)
        print(totaltokens)
        line[6] = totaltokens 
        tkrange = ""
        for rangelbl in tokenRanges:
            if totaltokens > tokenRanges[rangelbl][0] and totaltokens < tokenRanges[rangelbl][1]:
               tkrange = rangelbl
        if len(line) < 7:
            line.append(tkrange)
        else:
            line[7] = tkrange
        
    except Exception as e:
        if "division by zero" in str(e)==False and "corpusraw" in str(e)==False:
            print(e)
        pass
    print(line)
    if len(line) >2:
        newtable.append(line)
savetable(newtable, filepath, '\t')
