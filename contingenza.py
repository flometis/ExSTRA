#!/usr/bin/python3
import os
import os.path
import sys
import platform

#Input findings:
#File,Lemma,Occurrences,Language,LemmaID,Source,Tags,Author,Title,Gender,Year,Decade,Description
#Aleramo-Sibilla_Il-passaggio_1919.txt,editore,1,it,http://www.wikidata.org/entity/Q2516866,wikidata,rigaession,Aleramo Sibilla,Il passaggio,f,1919,1910_1919,persona che si occupa di pubblicare libri

#Input matadata:
#filename        autore  titolo  sesso   anno    decennio        tokens  range
#Carcano-Giulio_La_Nunziata_Novelle_Campagnuole_1842.txt Carcano, Giulio La nunziata     m       1842    1840_1849       101917  50_150mila

#Expected Info:
#anno;numerotesti;numerototaletokencorpora
#1840;3;13124

#Expected Freq:
#MESTIERE;1840;1842
#editore;occorrenzecolonna1840;occorrenzecolonna1842

def savetable(risultato, fileName = "risultato.csv", header = ""):
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


#File di input
metadatafile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Eltec100/Eltec-metadata.tsv"
text_file = open(metadatafile, "r", encoding='utf-8')
metadatastr = text_file.read()
text_file.close()
metadata = []
for row in metadatastr.split("\n"):
    metadata.append(row.split('\t'))
metadata = metadata[1:]

findingsfile = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Findings/exstra_dictionary_COMPLETE.tsv"
text_file = open(findingsfile, "r", encoding='utf-8')
findingsstr = text_file.read()
text_file.close()
findings = []
for row in findingsstr.split("\n"):
    findings.append(row.split('\t'))
findings = findings[1:]



#Le tabelle di contingenza hanno una variabile sulle righe e una sulle colonne. E un numero da leggere (di solito occorrenze). Es: lemma X anno
def tabellaContingenza(originale, variabileRighe, variabileColonne, numero):
    freq = {}
    colonne = []

    for r in range(len(findings)):
        row = findings[r]
        try:
            riga = row[variabileRighe]
            colonna = row[variabileColonne]
            if colonna not in colonne:
                colonne.append(colonna)
        except:
            continue
        try:
            occ = int(row[numero])
        except:
            continue
        if riga in freq:
            try:
                yocc = int(freq[riga][colonna])
            except:
                yocc = 0
            freq[riga][colonna] = yocc + occ
        else:
            freq[riga] = {colonna: occ}
    
    freqTable = []
    freqHeader = ["Variabile"]
    freqHeader.extend(colonne)
    freqTable.append(freqHeader)
    for riga in freq:
        fullrow = []
        fullrow.append(riga)
        for colonna in colonne:
            try:
                occ = int(freq[riga][colonna])
            except:
                occ = 0
            fullrow.append(occ)
        freqTable.append(fullrow)
    return freqTable

# Tabella di contingenza per le occorrenze
freqTable = tabellaContingenza(findings,1,10,2)
freqTable[0][0] = "MESTIERI"
print(freqTable[:10])
savetable(freqTable, "MESTIERIfreq.csv")

#Tabella riassuntiva per i metadati
info = {}
for r in range(len(metadata)):
    row = metadata[r]
    try:
        anno = str(row[4])
        tok = int(row[6])
    except:
        #print("Error on row "+str(row))
        continue
    if anno in info:
        info[anno][0] = int(info[anno][0]) + 1
        info[anno][1] = int(info[anno][1]) + tok
    else:
        info[anno] = [1, tok]
infoTable = []
infoTable.append(["Anno", "Testi", "Token"])
for anno in info:
    fullrow = [anno]
    fullrow.extend(info[anno])
    infoTable.append(fullrow)
print(infoTable[:10])
savetable(infoTable, "MESTIERIinfo.csv")
