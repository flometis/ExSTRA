#!/usr/bin/python3

import subprocess

#Gli argomenti forniti allo script sono contenuti nella lista sys.argv, e il primo elemento della lista è sempre il percorso completo dell'eseguibile. Quindi per scoprire la cartella in cui ci troviamo usiamo la funzione os.path.dirname (che ti fornisce il nome della cartella del file che le dai in pasto). Aggiungiamo os.path.abspath per essere sicuri che il risultato sia un percorso valido.
import os.path
import sys
import time
import os
import platform

#VARIABILI GLOBALI

so = platform.system()
if  so == "Windows":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-Win64/udpipe"  
elif so == "Linux":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-linux64/udpipe"
elif so == "Mac":
    eseguibile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/bin-osx/udpipe"
	#È chiaro che su Windows dovresti modificare il nome della cartella in bin-win64
#TODO: si può usare la funzione platform.system per riconoscere il sistema operativo (https://stackoverflow.com/a/1857). Si possono usare le condizioni if per creare il giusto percorso dell'eseguibile su ogni sistema.
modello = os.path.abspath(os.path.dirname(sys.argv[0])) + "/modelli/italian-isdt-ud-2.4-190531.udpipe"

dct = {"sindex" : 0, "tkn" : 1, "lemma" : 2, "POS" : 3, "RPOS" : 4, "morph" : 5 , "depA": 6, "depB": 7}
profs = {"url" : 0, "prof" : 1, "definition" : 2}

def patternfinder(corpus, patternlist):
    global eseguibile
    global modello
    global dct
    global profs
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
    
    listarisultati = []
    patterndict = {}
    mytable = stroutput.split("\n")
    patternlist = patternlist.split("\n")
    for prow in range(len(patternlist)):
        try:
            chiave = patternlist[prow].split(",")[profs["prof"]]
            valori = [patternlist[prow].split(",")[profs["url"]], patternlist[prow].split(",")[profs["definition"]]]
            patterndict[chiave] = valori
        except:
            continue
    #for prow in range(len(patternlist)):
   #     patternlist[prow] = patternlist[prow].split(",")[profs["prof"]]
    for row in range(len(mytable)):
        mytable[row] = mytable[row].split("\t") #creare lista di liste (tabella, riga, colonna)
        if len(mytable[row]) <8:
            continue
        lemma = mytable[row][dct["lemma"]]
        if lemma in patterndict:
            rigarisultato = [lemma]
            rigarisultato.extend(patterndict[lemma])
            listarisultati.append(rigarisultato)
        
    return listarisultati

#corpus = sys.argv[1]
#patternlist = sys.argv[2]

try:
    text_file = open(sys.argv[1], "r", encoding='utf-8')
    corpus = text_file.read()
    text_file.close()

    text_file = open(sys.argv[2], "r", encoding='utf-8')
    patternlist = text_file.read()
    text_file.close()

except:
    print("main.py corpus patternlist")
    sys.exit()

risultato = patternfinder(corpus, patternlist)
print(risultato)

#Trasformo la tabella in una stringa formato CSV
separatore = ","
stringarisultato = ""
for r in range(len(risultato)):
    for i in range(len(risultato[r])):
        if i > 0:
            stringarisultato = stringarisultato + separatore
        stringarisultato = stringarisultato + risultato[r][i]
    stringarisultato = stringarisultato + "\n"


#Scrivo la stringa in un file di testo CSV
fileName = "risultato.csv"
text_file = open(fileName, "w", encoding='utf-8')
text_file.write(stringarisultato)
text_file.close()
