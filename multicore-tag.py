#!/usr/bin/python3
# -*- coding: utf-8 -*-

# NOTA: questo script è stato testato solo su GNU/Linux

from os import path
import sys
import os
import time
import re
import subprocess
import tempfile
from threading import Thread
import signal
import os.path
import platform
import re
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

modello = os.path.abspath(os.path.dirname(sys.argv[0])) + "/modelli/italial-all.udpipe"

udlanguage = "ita"


if so == "Windows":
    branmain = branmain.replace("/", "\\")
    modello = modello.replace("/", "\\")


def execWithTimeout(mycmd, checkfile = "", mytimeout = 10, waitforstop = 10):
    global so
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



def escapeText(mytxt):
    newtxt = mytxt.replace("'","''")
    return newtxt



def tagText(filepath):
    global eseguibile
    global branmain
    global modello
    global udlanguage
    global so
    if so == "Windows":
        filepath = filepath.replace("/", "\\")
    if os.path.isfile(filepath) == False:
        return
    text_file = open(filepath, "r", encoding='utf-8')
    corpus = text_file.read()
    text_file.close()
    if filepath[-4:] == ".txt":
        taggedname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"+os.path.basename(filepath)[:-4]+"-bran.tsv"
        if not os.path.isdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/"):
            os.mkdir(os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/")
        so = platform.system()
        if so == "Windows":
            taggedname = taggedname.replace("/", "\\")
        if not os.path.isfile(taggedname):
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
            file.write(corpus)
            file.close()
            sessionfile = tmpdir+"/testo-bran.tsv"
            execWithTimeout(eseguibile+" "+branmain+" udpipeImport "+origfile+" \""+udlanguage+":"+modello+"\" n", sessionfile, -1, 20) #Se entro 20 minuti non ha finito il tag, il file deve avere qualche problema
            shutil.move(sessionfile, taggedname)
            shutil.rmtree(tmpdir)
            print("Written tagged output to: "+taggedname)
        else:
            print("Tagged corpus "+taggedname+" already exists, not tagging again.")

def bulktag(originals):
    if True:
        o = 0
        origAvailable = True
        while origAvailable:
            if o >= len(originals):
                origAvailable = False
                break
            
            try:
                 print(tbname+": "+str(o)+"/"+str(len(originals)))
            except:
                 pass
            threads = []
            
            #Add one thread per core
            of = o + cores
            if of > len(originals):
               of = len(originals)
            for ot in range(o,of):
                thisorig = originals[ot]
                print(thisorig)
                t = Thread(target=tagText, args=(thisorig,))
                threads.append(t)

            # Start all threads
            for x in threads:
                x.start()
            
            # Wait for all of them to finish
            for x in threads:
                x.join()

            #Ready for next cycle
            o = of
        


# Se interrotto, pulire tutti i thread appesi con
# for k in $(ps aux | grep udpipeImport | grep -o 'root *[0-9]*' | grep -o '[0-9]*');do kill -9 $k; done


filenames = []
path = sys.argv[1]
if os.path.isfile(path) == True:
    filenames.append(path)

if os.path.isdir(path) == True:
    filenames = [os.path.abspath(path + "/" + filename) for filename in os.listdir(path)]


try:
    #Get total number of cpu cores
    cores_available = len(os.sched_getaffinity(0))
    cores = int(cores_available*(3/4))
    if cores < 2:
        cores = 2
#cores = 8
except:
    cores = 2


#if not os.path.exists('/tmp/Bran'):
#    os.makedirs('/tmp/Bran')
#os.system("rm /tmp/Bran/* 2> /dev/null")


bulktag(filenames)
