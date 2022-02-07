import subprocess

import os.path
import sys
import time
import os
import platform
import re

#VARIABILI GLOBALI

pythonexe = "python3"
so = platform.system()
if  so == "Windows":
    pythonexe = "python"

rmexe = "rm"
so = platform.system()
if  so == "Windows":
    rmexe = "del"

print("Do you want to clean up original texts? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " pulisci.py")
print("Do you want to tag again all texts? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    #os.system(rmexe+" "+os.path.abspath(os.path.dirname(sys.argv[0]))+"/Tagged/*.tsv")
    os.system(pythonexe+ " clean-metadata.py --force")
print("Do you want to count tokens again? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " clean-metadata.py")

print("Do you want to update ExSTRA dictionary? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " extract-dictionary.py all it")

print("Running again ExSTRA")
os.system(pythonexe+ " exstra.py Eltec100/puliti it")

os.system(pythonexe+ " contingenza.py")

