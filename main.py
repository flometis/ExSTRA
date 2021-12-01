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

print("Do you want to clean up original texts? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " pulisci.py")
print("Do you want to tag again all texts? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " clean-metadata.py --force")
print("Do you want to check metadata integrity? [y/N]")
rch = input()
if rch == "Y" or rch == "y":
    os.system(pythonexe+ " clean-metadata.py")

#print("Do you want to build again ExSTRA dictionary? [y/N]")
#rch = input()
#if rch == "Y" or rch == "y":
#    os.system(pythonexe+ " extract-dictionary.py")

print("Running again ExSTRA")
os.system(pythonexe+ " exstra.py Eltec100/puliti it")

os.system(pythonexe+ " contingenza.py")

