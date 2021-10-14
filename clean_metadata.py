#!/usr/bin/bash

import subprocess
import os.path
import sys
import time
import os
import platform
import re
import psutil

path = "Eltec100/Eltec100"
filenames = [filename for filename in os.listdir(path)]

filepath = "Eltec100/Eltec-metadata.tsv"
text_file = open(filepath, "r", encoding='utf-8')
text = text_file.read()
text_file.close()

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

def savetable(risultato, fileName = "risultato.csv", separatore = ",", header = ""):
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
for r in range(len(text.split('\n'))):
    row = text.split('\n')[r]
    line = row.split('\t')
    if r > 0:
        line[0] = line[0].replace(".xml","")
        line[0] = re.sub('[^a-z]' , '',line[0].lower())
    for file in filenames:
        fileclean = re.sub('[^a-z]' , '',file.lower())
        if fileclean.startswith(line[0]):
            line[0] = file
    #Conteggio tokens
    try:
        tnum = int(line[6])
    except:
        tnum = 0
    try:
        if tnum > 0 or len(line)<2:
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
        corpusfile = UDtagger(corpusraw)
        corpuslist = corpusfile.split("\n")
        for u in range(len(corpuslist)):
            udline = corpuslist[u]
            #L'idea è che le righe che contengono token iniziano con un numero o al massimo con una serie di numeri separati da -
            tmptokens = ""
            try:
                tmptokens = udline[:udline.index('\t')]
                test = int(tmptokens)
                totaltokens = totaltokens + 1
            except:
                elements = tmptokens.count("-") +1 #se la parola è composta ho un -, per esempio 11-12, quindi avrò 2 righe superflue
                if elements >1:
                    totaltokens = totaltokens - elements
                pass
        print(totaltokens)
        line[6] = totaltokens 
    except Exception as e:
        if "division by zero" in str(e)==False and "corpusraw" in str(e)==False:
            print(e)
        pass
    print(line)
    if len(line) >2:
        newtable.append(line)
savetable(newtable, filepath, '\t')
