# Extracting social STatus Ranks Automatically

## Pipeline

The complete pipeline is implemented in **main.py**, you can just run this file if you need to do every step.
Otherwise, here you can find the list of steps so you can run them manually one at a time.


1. (optional) Clean up original texts
This should only be done if you plan to use a new corpus: clean up common OCR errors and dirty bytes:
```
python3 pulisci.py
```

2. (optional) Update metadata
This should only be done if you plan to use a new corpus: please add its metadata in **Eltec100/Eltec-metadata.tsv**, then run
```
python3 clean-metadata.py
```
To force tagging again already tagged corpus add --force as last argument:
```
python3 clean-metadata.py --force
```


3. (optional) Generate new ExSTRA dictionary
```
python3 extract-dictionary.py
```
At this moment, this is an interactive tool: answer to the questions to get the lemmas you want.

4. Extract lemma occurrences
If you need to tag again your corpus, please remove files inside ***Tagged*** folder (rm Tagged/*).
```
#python3 main.py corpus [languages] [patternlist]
python3 exstra.py Eltec100/puliti it
```
languages should be separated by commas (es: it,en,scn).

patternlist is list of entities to find (exstra_dictionary is default, but you might generate a subset and use it)

corpus can be:
* single .xml/.txt file;
* folder containing .xml/.txt files from the ELTeC Corpus;
* folder containing .tsv files already tagged with UDpipe

5. Generate simple plot report
```
cd plots/histogram-decades
C:\Program Files\R\R-4.1.1\bin\Rscript.exe occ-decades.R
```
For this to work you'll need R and Rscript (https://cran.r-project.org/bin/windows/base/, or ***apt-get install R*** on Debian).

6. Generate contingency table
If you need a contingency table, you should run
```
python3 contingenza.py
```
The script, at this moment, builds a lemmaXyear table, but you can easily change the code to set different variable for rows and columns.

## TODO
- [ ] Make extract-dictionary.py non interactive
- [x] Add sapere.it lemmas in exstra-dictionary.csv
- [ ] Change every CSV to TSV
- [x] Perform UDtagging only if needed (main.py)
- [ ] Improve speed for occurrences finder (main.py)
- [ ] Add synonims from wikitionary for every wikidata lemma
- [ ] Tidy up repository

## Sources
* Sapere.it
* Wikidata
* Wikitionary (TODO)
