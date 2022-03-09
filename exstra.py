#!/usr/bin/python3

import subprocess

#Gli argomenti forniti allo script sono contenuti nella lista sys.argv, e il primo elemento della lista è sempre il percorso completo dell'eseguibile. Quindi per scoprire la cartella in cui ci troviamo usiamo la funzione os.path.dirname (che ti fornisce il nome della cartella del file che le dai in pasto). Aggiungiamo os.path.abspath per essere sicuri che il risultato sia un percorso valido.
import os.path
import sys
import time
import os
import platform
import re
import tempfile
import subprocess
import signal
import shutil

#VARIABILI GLOBALI
so = platform.system()
if  so == "Windows":
    eseguibile = "C:\\Python37\\python.exe"
elif so == "Linux":
    eseguibile = '/usr/bin/python3'
elif so == "Mac":
    eseguibile = '/usr/bin/python3'

#Mi aspetto di trovare la cartella di Bran nella stessa cartella di ExSTRA (es: Documents/GitHub/ExSTRA, Documents/GitHub/Bran)
branmain = os.path.dirname(os.path.abspath(os.path.dirname(sys.argv[0]))) + '/Bran/main.py'

#TODO: passare un modello a Bran 
modello = os.path.abspath(os.path.dirname(sys.argv[0])) + "/modelli/italial-all.udpipe"

if so == "Windows":
    branmain = branmain.replace("/", "\\")
if so == "Windows":
    modello = modello.replace("/", "\\")

corpuscols = {'TAGcorpus': 0,'token': 1,'lemma': 2,'pos': 3,'ner': 4,'feat': 5,'IDword': 6,'IDphrase': 7,'dep': 8,'head': 9}
profs = {"url" : 0, "prof" : 1, "source": 2 , "lang": 3 , "tag": 4, "definition" : 5}


patterndict = {}
ngramsdict = {}



metadatafile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Eltec100/Eltec-metadata.tsv"
text_file = open(metadatafile, "r", encoding='utf-8')
metadatastr = text_file.read()
text_file.close()
metadata = []
for row in metadatastr.split("\n"):
    metadata.append(row.split('\t'))
metadata = metadata[1:]


def execWithTimeout(mycmd, checkfile = "", mytimeout = 10, waitforstop = 10):
    redirect = ""
    if so == "Linux":
      redirect = " &> /dev/null"
    a = subprocess.Popen(mycmd + redirect, stdout=subprocess.PIPE, shell=True)
    starttime = time.time()
    if checkfile != "":
        while os.path.isfile(checkfile)==False:
           if (time.time() - starttime) > (mytimeout) and mytimeout > 0:
               time.sleep(1)
               break
           time.sleep(0.5)
    if mytimeout < 1:
        mytimeout = waitforstop
    while a.poll():
        if (time.time() - starttime) > mytimeout:
            time.sleep(1)
            break
        else:
            time.sleep(0.5)
    #Safety measure: do not proceed immediately, os might still be writing the file
    while (time.time()-os.path.getmtime(checkfile)<waitforstop):
        time.sleep(0.5)
    try:
        #subprocess.Popen.kill(a)
        os.kill(a.pid, signal.SIGKILL)
    except:
        if so == "Linux":
            try:
                os.system("kill -9 $(ps aux | grep '"+mycmd+"' | grep -o 'root *[0-9]*' | grep -o '[0-9]*' 2> /dev/null) 2> /dev/null")
            except:
                pass

def dictGenerator(patternlist, languages = ""):
    global patterndict
    global ngramsdict
    patternlist = patternlist.split("\n")
    #Realizzo un dizionario per accesso rapido alle informazioni
    for prow in range(len(patternlist)):
        try:
            sep = '\t'
            chiave = patternlist[prow].split(sep)[profs["prof"]]
            try:
                valori = [patternlist[prow].split(sep)[profs["url"]], patternlist[prow].split(sep)[profs["source"]], patternlist[prow].split(sep)[profs["tag"]], patternlist[prow].split(sep)[profs["definition"]]]
            except IndexError:
                valori = [patternlist[prow].split(sep)[profs["url"]], patternlist[prow].split(sep)[profs["source"]], patternlist[prow].split(sep)[profs["tag"]], ""]
            lingua = patternlist[prow].split(sep)[profs["lang"]]
            if languages != "":
                if lingua not in languages.split(","):
                    continue
            if " " in chiave:
                #TODO: lemmatizzare chiave
                if chiave in ngramsdict:
                    ngramsdict[chiave][lingua] = valori
                else:
                    ngramsdict[chiave] = {lingua: valori}
            else:
                if chiave in patterndict:
                    patterndict[chiave][lingua] = valori
                else:
                    patterndict[chiave] = {lingua: valori}
        except Exception as e:
            #print(e)
            continue
    print("Lemmas: "+str(len(patterndict)))
    print("Ngrams: "+str(len(ngramsdict)))

def patternfinder(filepath, stroutput, patternlist, languages = ""):
    global corpuscols
    global profs
    global metadata
    global eseguibile
    global branmain
    global patterndict
    global ngramsdict

    listarisultati = []
    fileinfo = ['','','','','']
    for mrow in metadata:
        if re.sub("[^a-z0-9]","",mrow[0].lower()[:-4]) == re.sub("[^a-z0-9]","",os.path.basename(filepath).lower()[:-4]):
            fileinfo[0] = mrow[1].replace(",","")
            fileinfo[1] = mrow[2].replace(",","")
            fileinfo[2] = mrow[3]
            fileinfo[3] = mrow[4]
            fileinfo[4] = mrow[5]
    mytable = stroutput.split("\n")
    #Conto le occorrenze
    occ = {}
    #Lemma
    for row in range(len(mytable)):
        mytable[row] = mytable[row].split("\t") #creare lista di liste (tabella, riga, colonna)
        if len(mytable[row]) <8:
            continue
        lemma = mytable[row][corpuscols["lemma"]]
        if lemma in patterndict and "NOUN" in mytable[row][corpuscols["pos"]]:
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
    #Ngram:
    if so == "Windows":
        os.makedirs("C:\Temp\Bran", exist_ok=True)
        tmpdir = tempfile.NamedTemporaryFile(dir="C:\Temp\Bran").name
    else:
        os.makedirs("/tmp/Bran", exist_ok=True)
        tmpdir = tempfile.NamedTemporaryFile(dir="/tmp/Bran").name
    os.makedirs(tmpdir)
    sessionfile = tmpdir+"/testo-bran.tsv"
    taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(filepath)[:-4]+"-bran.tsv"
    shutil.copy(taggedname, sessionfile)
    useFilter = False
    if useFilter:
        for ngram in ngramsdict:
            mycol = 1
            hkey = "token"
            filtertext = ""
            for iNG in range(len(ngram.split(" "))):
                elNgram = ngram.split(" ")[iNG]
                if iNG > 0:
                    filtertext = filtertext + "&&"
                filtertext = filtertext + "lemma["+str(iNG)+"]=^"+elNgram.replace("'","").replace('"','')+"$"
            if filtertext == "":
                continue
            #print(filtertext)
            cleanedfilter = re.sub("[^a-zA-Z0-9\[\]]", "", filtertext)[:50]
            output = sessionfile + "-cerca-" + hkey + "-filtro-" + cleanedfilter + ".tsv"
            #print(output)
            execWithTimeout(eseguibile+" "+branmain+" cerca "+sessionfile+" "+ str(mycol) + " '" + filtertext +"' n", output, -1, 0.5)
            ngOcc = 0
            with open(output, "r", encoding='utf-8') as ins:
                for line in ins:
                    ngOcc = ngOcc +1
            ngOcc = ngOcc -1
            if ngOcc > 0:
                #print("Ngram occurrences: "+str(ngOcc))
                #occ[ngram] = ngOcc
                #Aggiungo una riga per ogni lingua in cui esiste il lemma
                for lingua in ngramsdict[ngram]:
                     rigarisultato = [os.path.basename(filepath), ngram]
                     rigarisultato.append(ngOcc)
                     rigarisultato.append(lingua)
                     rigarisultato.extend(ngramsdict[ngram][lingua][:-1])
                     rigarisultato.extend(fileinfo)
                     rigarisultato.append(ngramsdict[ngram][lingua][-1])
                     listarisultati.append(rigarisultato)
    else:
        mycol = 2
        hkey = "lemma"
        output = sessionfile + "-ricostruito-" + hkey + "-.txt"
        #execWithTimeout(eseguibile+" "+branmain+" ricostruisci "+sessionfile+" "+ str(mycol) + " n '' n", output, -1, 0.5)
        execWithTimeout(eseguibile+" "+branmain+" ricostruisci "+sessionfile+" "+ str(mycol), output, -1, 0.5)
        text_file = open(output, "r", encoding='utf-8')
        rebuiltCorpus = text_file.read()
        text_file.close()
        #print(output)
        for ngram in ngramsdict:
            #we're looking for non overlapping occurrences 
            #ngOcc = rebuiltCorpus.count(ngram)  #questo da problemi con iniziali e finali delle parole. Es: "re consorte" viene trovato in "essere consorte"
            myregex = "[^A-Za-zàèéòìù]"+re.escape(ngram)+"[^A-Za-zàèéòìù]"
            ngOcc = len(re.findall(myregex, rebuiltCorpus))
            if ngOcc > 0:
                #Aggiungo una riga per ogni lingua in cui esiste il lemma
                for lingua in ngramsdict[ngram]:
                     rigarisultato = [os.path.basename(filepath), ngram]
                     rigarisultato.append(ngOcc)
                     rigarisultato.append(lingua)
                     rigarisultato.extend(ngramsdict[ngram][lingua][:-1])
                     rigarisultato.extend(fileinfo)
                     rigarisultato.append(ngramsdict[ngram][lingua][-1])
                     listarisultati.append(rigarisultato)
    shutil.rmtree(tmpdir)
    return listarisultati

def savetable(risultato, fileName = "risultato.tsv"):
    header = "File\tLemma\tOccurrences\tLanguage\tLemmaID\tSource\tTags\tAuthor\tTitle\tGender\tYear\tDecade\tDescription\n"
    separatore = "\t"
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

patternlistFile = os.path.abspath(os.path.dirname(sys.argv[0])) + "/exstra_dictionary.tsv" 
if len(sys.argv) >3:
    patternlistFile = sys.argv[3]

text_file = open(patternlistFile, "r", encoding='utf-8')
patternlist = text_file.read()
text_file.close()

fullresults = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/"+os.path.basename(patternlistFile)[:-4]+"_COMPLETE.tsv"


filenames = []
path = sys.argv[1]
if os.path.isfile(path) == True:
    filenames.append(path)

if os.path.isdir(path) == True:
    filenames = [os.path.abspath(path + "/" + filename) for filename in os.listdir(path)]

dictGenerator(patternlist, chooseLang)

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
        taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(filepath)[:-4]+"-bran.tsv"
        if not os.path.isdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"):
            os.mkdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/")
        so = platform.system()
        if so == "Windows":
            taggedname = taggedname.replace("/", "\\")
        if not os.path.isfile(taggedname):
            #corpusfile = UDtagger(corpusraw)
            if so == "Windows":
                os.makedirs("C:\Temp\Bran", exist_ok=True)
                tmpdir = tempfile.NamedTemporaryFile(dir="C:\Temp\Bran").name
            else:
                os.makedirs("/tmp/Bran", exist_ok=True)
                tmpdir = tempfile.NamedTemporaryFile(dir="/tmp/Bran").name
            os.makedirs(tmpdir)
            origfile = tmpdir+"/testo.txt"
            print("Tagging file in temporary folder "+tmpdir)
            file = open(origfile,"w", encoding='utf-8')
            file.write(corpusraw)
            file.close()
            sessionfile = tmpdir+"/testo-bran.tsv"
            execWithTimeout(eseguibile+" "+branmain+" udpipeImport "+origfile+" 'ita:"+modello+"' n", sessionfile, -1, 20) #Se entro 20 minuti non ha finito il tag, il file deve avere qualche problema
            shutil.move(sessionfile, taggedname)
            shutil.rmtree(tmpdir)
            print("Written tagged output to: "+taggedname)
        else:
            print("Tagged corpus "+taggedname+" already exists, not tagging again.")
        text_file = open(taggedname, "r", encoding='utf-8')
        corpusfile = text_file.read()
        text_file.close()
    elif filepath[-4:] == ".tsv":
        corpusfile = corpus
    else:
        continue
    risultato = patternfinder(filepath, corpusfile, patternlist, chooseLang)
    risultati.extend(risultato)
#Trasformo la tabella in una stringa formato CSV
    newname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/"+os.path.basename(patternlistFile)[:-4]+"_"+os.path.basename(filepath)[:-4]+".tsv"
    savetable(risultato, newname)
    savetable(risultati, fullresults)
    print("Results for this file in: "+newname)
print("Complete results in: "+fullresults)
