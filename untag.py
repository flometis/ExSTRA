#!/usr/bin/python3
import re
import sys


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


text_file = open(sys.argv[1], "r", encoding='utf-8')
corpus = text_file.read()
text_file.close()

corpus = untagRegex(corpus)

fileName = sys.argv[1]+".txt"
text_file = open(fileName, "w", encoding='utf-8')
text_file.write(corpus)
text_file.close()
