#!/usr/bin/python3

import subprocess

#Gli argomenti forniti allo script sono contenuti nella lista sys.argv, e il primo elemento della lista è sempre il percorso completo dell'eseguibile. Quindi per scoprire la cartella in cui ci troviamo usiamo la funzione os.path.dirname (che ti fornisce il nome della cartella del file che le dai in pasto). Aggiungiamo os.path.abspath per essere sicuri che il risultato sia un percorso valido.
import os.path
import sys
import time
import os
import platform
import re

#VARIABILI GLOBALI

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
profs = {"url" : 0, "prof" : 1, "definition" : 2}

def UDtagger(origcorpus):
    global eseguibile
    global modello
    #Udpipe andrebbe lanciato con un comando del tipo ./bin-linux64/udpipe --tokenize --tag --parse ./modelli/italian-isdt-ud-2.4-190531.udpipe
    #Per poterlo avviare da Python con la libreria Subprocess dobbiamo dividere i vari argomenti in elementi di una lista, così non ci sono spazi
    process = subprocess.Popen([eseguibile, "--tokenize", "--tag", "--parse", modello], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    #Per lavorare sullo standard input bisogna usare una sequenza di byte invece di una comune stringa di testo, perché siamo a basso livello. Una stringa può essere codificata come byte usando la sua funzione encode
    testobyte = corpus.encode(encoding='utf-8')
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
    
def patternfinder(stroutput, patternlist):
    global dct
    global profs
    listarisultati = []
    patterndict = {}
    mytable = stroutput.split("\n")
    patternlist = patternlist.split("\n")
    #Realizzo un dizionario per accesso rapido alle informazioni
    for prow in range(len(patternlist)):
        try:
            chiave = patternlist[prow].split(",")[profs["prof"]]
            valori = [patternlist[prow].split(",")[profs["url"]], patternlist[prow].split(",")[profs["definition"]]]
            patterndict[chiave] = valori
        except:
            continue
    #for prow in range(len(patternlist)):
    #     patternlist[prow] = patternlist[prow].split(",")[profs["prof"]]

    #Conto le occorrenze
    occ = {}
    for row in range(len(mytable)):
        mytable[row] = mytable[row].split("\t") #creare lista di liste (tabella, riga, colonna)
        if len(mytable[row]) <8:
            continue
        lemma = mytable[row][dct["lemma"]]
        if lemma in patterndict and "NOUN" in mytable[row][dct["POS"]]:
            try:
                occ[lemma] = occ[lemma] +1
            except:
                occ[lemma] = 1
            rigarisultato = [lemma]
            rigarisultato.append(occ[lemma])
            rigarisultato.extend(patterndict[lemma])
            listarisultati.append(rigarisultato)
        
    return listarisultati

def savetable(risultato, fileName = "risultato.csv"):
    separatore = ","
    stringarisultato = ""
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

def untagRegex(mytext):
    textIndexes = [(m.start(0), m.end(0)) for m in re.finditer("\<text\>.*?\<\/text\>", mytext, flags=re.DOTALL)] # we want only what's inside <text></text> tags
    newtext = ""
    #we might have many text portions in the same file, we just concatenate them
    for subtextIndex in textIndexes:
        start = subtextIndex[0]
        end = subtextIndex[1]
        newtext = newtext + mytext[start:end]
    newtext = re.sub("\<.*?\>", "", newtext)  #substitute tags with nothing
    newtext = re.sub(" +", " ", newtext)  #substitute multiple spaces with one space
    newtext = re.sub("\n *\n", "\n", newtext)  #substitute multiple newlines
    newtext = re.sub("([^\.\!\?])\n([^A-Z])", "\g<1> \g<2>", newtext)  #substitute spaces at the beginning of every row with nothing
    return newtext

if len(sys.argv) <3:
    print("main.py corpus patternlist")
    print("patternlist is list of entities to find")
    print("corpus can be:\n1) single .xml file;\n2) folder containing .xml files from the ELTeC Corpus;\n3) folder containing .tsv files already tagged with UDpipe")
    sys.exit()

text_file = open(sys.argv[2], "r", encoding='utf-8')
patternlist = text_file.read()
text_file.close()

filenames = []
path = sys.argv[1]
if os.path.isfile(path) == True:
    filenames.append(path)

if os.path.isdir(path) == True:
    filenames = [os.path.abspath(path + "/" + filename) for filename in os.listdir(path)]

for filepath in filenames:
    if os.path.isfile(filepath) == False:
        continue
    text_file = open(filepath, "r", encoding='utf-8')
    corpus = text_file.read()
    text_file.close()
    if filepath[-4:] == ".xml":
        corpusraw = untagRegex(corpus)
        corpusfile = UDtagger(corpusraw)
        taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(filepath)[:-4]+".tsv"
        text_file = open(taggedname, "w", encoding='utf-8')
        text_file.write(corpusfile)
        text_file.close()
    elif filepath[-4:] == ".tsv":
        corpusfile = corpus
    else:
        continue
    risultato = patternfinder(corpusfile, patternlist)
#Trasformo la tabella in una stringa formato CSV
    newname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/"+os.path.basename(sys.argv[2])[:-4]+"_"+os.path.basename(filepath)[:-4]+".csv"
    savetable(risultato, newname)
