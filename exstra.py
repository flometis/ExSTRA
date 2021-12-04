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
profs = {"url" : 0, "prof" : 1, "source": 2 , "lang": 3 , "tag": 4, "definition" : 5}

metadatafile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Eltec100/Eltec-metadata.tsv"
text_file = open(metadatafile, "r", encoding='utf-8')
metadatastr = text_file.read()
text_file.close()
metadata = []
for row in metadatastr.split("\n"):
    metadata.append(row.split('\t'))
metadata = metadata[1:]


def UDtagger(origcorpus):
    global eseguibile
    global modello
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
    
def patternfinder(filepath, stroutput, patternlist, languages = ""):
    global dct
    global profs
    global metadata
    listarisultati = []
    fileinfo = ['','','','','']
    for mrow in metadata:
        if re.sub("[^a-z0-9]","",mrow[0].lower()[:-4]) == re.sub("[^a-z0-9]","",os.path.basename(filepath).lower()[:-4]):
            fileinfo[0] = mrow[1].replace(",","")
            fileinfo[1] = mrow[2].replace(",","")
            fileinfo[2] = mrow[3]
            fileinfo[3] = mrow[4]
            fileinfo[4] = mrow[5]
    patterndict = {}
    mytable = stroutput.split("\n")
    patternlist = patternlist.split("\n")
    #Realizzo un dizionario per accesso rapido alle informazioni
    for prow in range(len(patternlist)):
        try:
            chiave = patternlist[prow].split(",")[profs["prof"]]
            valori = [patternlist[prow].split(",")[profs["url"]], patternlist[prow].split(",")[profs["source"]], patternlist[prow].split(",")[profs["tag"]], patternlist[prow].split(",")[profs["definition"]]]
            lingua = patternlist[prow].split(",")[profs["lang"]]
            if languages != "":
                if lingua not in languages.split(","):
                    continue
            if chiave in patterndict:
                patterndict[chiave][lingua] = valori
            else:
                patterndict[chiave] = {lingua: valori}
        except:
            continue
    #Conto le occorrenze
    occ = {}
    for row in range(len(mytable)):
        mytable[row] = mytable[row].split("\t") #creare lista di liste (tabella, riga, colonna)
        if len(mytable[row]) <8:
            continue
        lemma = mytable[row][dct["lemma"]]
        if lemma in patterndict and "NOUN" in mytable[row][dct["POS"]]:
            #Non ho modo di sapere quale sia la lingua del lemma, assegno le stesse occorrenze a tutte le lingue disponibili
            try:
                occ[lemma] = occ[lemma] +1
            except:
                occ[lemma] = 1
            #Aggiungo una riga per ogni lingua in cui esiste il lemma
            for lingua in patterndict[lemma]:
                if occ[lemma] == 1:
                    rigarisultato = [os.path.basename(filepath), lemma]
                    rigarisultato.append(occ[lemma])
                    rigarisultato.append(lingua)
                    rigarisultato.extend(patterndict[lemma][lingua][:-1])
                    rigarisultato.extend(fileinfo)
                    rigarisultato.append(patterndict[lemma][lingua][-1])
                    listarisultati.append(rigarisultato)
                else:
                    for resRow in range(len(listarisultati)):
                        if listarisultati[resRow][1] == lemma and listarisultati[resRow][0] == os.path.basename(filepath) and listarisultati[resRow][3] == lingua:
                            listarisultati[resRow][2] = occ[lemma]
    return listarisultati

def savetable(risultato, fileName = "risultato.csv"):
    header = "File,Lemma,Occurrences,Language,LemmaID,Source,Tags,Author,Title,Gender,Year,Decade,Description\n"
    separatore = ","
    stringarisultato = header
    for r in range(len(risultato)):
        for i in range(len(risultato[r])):
            if i > 0:
                stringarisultato = stringarisultato + separatore
            stringarisultato = stringarisultato + str(risultato[r][i])
        stringarisultato = stringarisultato + "\n"
    #Scrivo la stringa in un file di testo CSV
    so = platform.system()
    if so == "Windows":
        fileName = fileName.replace("/", "\\")
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

if len(sys.argv) <2:
    print("main.py corpus [languages] [patternlist]")
    print("languages should be separated by commas")
    print("patternlist is list of entities to find (exstra_dictionary is default, but you might generate a subset and use it)")
    print("corpus can be:\n1) single .xml/.txt file;\n2) folder containing .xml/.txt files from the ELTeC Corpus;\n3) folder containing .tsv files already tagged with UDpipe")
    sys.exit()
if len(sys.argv) >2:
    chooseLang = sys.argv[2]
else:
    chooseLang = ""

patternlistFile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/exstra_dictionary.csv" 
if len(sys.argv) >3:
    patternlistFile = sys.argv[3]

text_file = open(patternlistFile, "r", encoding='utf-8')
patternlist = text_file.read()
text_file.close()

fullresults = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/"+os.path.basename(patternlistFile)[:-4]+"_COMPLETE.csv"


filenames = []
path = sys.argv[1]
if os.path.isfile(path) == True:
    filenames.append(path)

if os.path.isdir(path) == True:
    filenames = [os.path.abspath(path + "/" + filename) for filename in os.listdir(path)]

risultati = []
for filepath in filenames:
    if so == "Windows": 
        filepath = filepath.replace("/", "\\")
    if os.path.isfile(filepath) == False:
        continue
    text_file = open(filepath, "r", encoding='utf-8')
    corpus = text_file.read()
    text_file.close()
    if filepath[-4:] == ".xml" or filepath[-4:] == ".txt":
        corpusraw = corpus
        if filepath[-4:] == ".xml":
            corpusraw = untagRegex(corpus)
        if corpusraw == "":
            corpusraw = corpus
        taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(filepath)[:-4]+".tsv"
        if not os.path.isdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"):
            os.mkdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/")
        so = platform.system()
        if so == "Windows":
            taggedname = taggedname.replace("/", "\\")
        if not os.path.isfile(taggedname):
            corpusfile = UDtagger(corpusraw)
        else:
            print("Tagged corpus "+taggedname+" already exists, not tagging again.")
            text_file = open(taggedname, "r", encoding='utf-8')
            corpusfile = text_file.read()
            text_file.close()
        text_file = open(taggedname, "w", encoding='utf-8')
        text_file.write(corpusfile)
        text_file.close()
    elif filepath[-4:] == ".tsv":
        corpusfile = corpus
    else:
        continue
    risultato = patternfinder(filepath, corpusfile, patternlist, chooseLang)
    risultati.extend(risultato)
#Trasformo la tabella in una stringa formato CSV
    newname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/"+os.path.basename(patternlistFile)[:-4]+"_"+os.path.basename(filepath)[:-4]+".csv"
    savetable(risultato, newname)
    savetable(risultati, fullresults)
    print("Results for this file in: "+newname)
print("Complete results in: "+fullresults)
