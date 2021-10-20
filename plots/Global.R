# Caricamento librerie
library(ca)
library(shiny)
library(shinydashboard)
# Inizializzazione parametri di base
source("Parameters.R")
metadataFile <- paste(metadataFolder, metadataFileName, sep = "/")

# Caricamento file metadati
metaData <- read.table(file = metadataFile, sep = "\t", header = TRUE)
# Tengo solo gli autori da analizzare
# metaData <- metaData[metaData$titolo %in% titles,]

# Caricamento testi
# tdm <- read.table(file = filesList, header = T, sep = ",")
listOfTexts <- list.files(path = textFolder, pattern = "exstra_dictionary_COMPLETE.csv")
textsToLoad <- paste(textFolder, listOfTexts, sep = "")
for(tx in textsToLoad){
  print(tx)
  print(which(tx == textsToLoad))
  if(which(tx == textsToLoad) == 1) {
    tdm <- read.table(file = tx, sep = ",", header = TRUE, quote = "'")
  } else {
    txt <- read.table(file = tx, sep = ",", header = TRUE, quote = "'")
    tdm <- rbind(tdm, txt)
  }
}
# rm(txt)

# Tengo solo le lingue in analisi
tdm <- tdm[tdm$Language %in% languages,]

# Calcolo le frequenze relativef
metadataOccurrences <- data.frame(filename = metaData$filename, Tokens = metaData$tokens) 
tdm <- merge(x = tdm, y = metadataOccurrences, by.x = "File", by.y = "filename", all.x = TRUE)
tdm$Occurrences <- tdm$Occurrences / tdm$Tokens
rm(metadataOccurrences)


# Faccio pivot della term document matrix - per libro
tdm_pivot_book <- tdm[,c(9,2:3)]
tdm_pivot_book <- reshape(data = tdm_pivot_book, idvar = "Lemma", timevar = "Title", direction = "wide")
tdm_pivot_book[is.na(tdm_pivot_book)]<-0
# Rinomino i campi, come i testi
names(tdm_pivot_book) <- c("Lemma", sort(metaData$titolo))

# Faccio pivot della term document matrix - per autore
tdm_pivot_author <- tdm[,c(8,2,3)]
tdm_pivot_author <- aggregate(x = tdm_pivot_author$Occurrences, by = list(tdm_pivot_author$Lemma, tdm_pivot_author$Author), FUN = sum)
tdm_pivot_author <- data.frame(Lemma = tdm_pivot_author$Group.1, Author = tdm_pivot_author$Group.2, Occurrences = tdm_pivot_author$x)
tdm_pivot_author <- reshape(data = tdm_pivot_author, idvar = "Lemma", timevar = "Author", direction = "wide")
tdm_pivot_author[is.na(tdm_pivot_author)]<-0
# Rinomino i campi, come i testi
names(tdm_pivot_author) <- c("Lemma", sort(unique(metaData$autore)))

# Faccio pivot della term document matrix - per sesso
tdm_pivot_gender <- tdm[,c(10,2,3)]
tdm_pivot_gender <- aggregate(x = tdm_pivot_gender$Occurrences, by = list(tdm_pivot_gender$Lemma, tdm_pivot_gender$Gender), FUN = sum)
tdm_pivot_gender <- data.frame(Lemma = tdm_pivot_gender$Group.1, Gender = tdm_pivot_gender$Group.2, Occurrences = tdm_pivot_gender$x)
tdm_pivot_gender <- reshape(data = tdm_pivot_gender, idvar = "Lemma", timevar = "Gender", direction = "wide")
tdm_pivot_gender[is.na(tdm_pivot_gender)]<-0
# Rinomino i campi, come i testi
names(tdm_pivot_gender) <- c("Lemma", sort(unique(metaData$sesso)))

# Faccio pivot della term document matrix - per decennio
tdm_pivot_decade <- tdm[,c(12,2,3)]
tdm_pivot_decade <- aggregate(x = tdm_pivot_decade$Occurrences, by = list(tdm_pivot_decade$Lemma, tdm_pivot_decade$Decade), FUN = sum)
tdm_pivot_decade <- data.frame(Lemma = tdm_pivot_decade$Group.1, Decade = tdm_pivot_decade$Group.2, Occurrences = tdm_pivot_decade$x)
tdm_pivot_decade <- reshape(data = tdm_pivot_decade, idvar = "Lemma", timevar = "Decade", direction = "wide")
tdm_pivot_decade[is.na(tdm_pivot_decade)]<-0
# Rinomino i campi, come i testi
names(tdm_pivot_decade) <- c("Lemma", sort(unique(metaData$decennio)))


# Faccio pivot della term document matrix - per anno
tdm_pivot_year <- tdm[,c(11,2,3)]
tdm_pivot_year <- aggregate(x = tdm_pivot_year$Occurrences, by = list(tdm_pivot_year$Lemma, tdm_pivot_year$Year), FUN = sum)
tdm_pivot_year <- data.frame(Lemma = tdm_pivot_year$Group.1, Year = tdm_pivot_year$Group.2, Occurrences = tdm_pivot_year$x)
tdm_pivot_year <- reshape(data = tdm_pivot_year, idvar = "Lemma", timevar = "Year", direction = "wide")
tdm_pivot_year[is.na(tdm_pivot_year)]<-0
# Rinomino i campi, come i testi
names(tdm_pivot_year) <- c("Lemma", sort(unique(metaData$anno)))

# Costruzione della matrice Variabile-Etichette
listOfValues <- character()
listOfVariables_idx <- character()
for(varb in listOfVariables){
  listOfValues <- c(listOfValues,unique(metaData[[varb]]))
  listOfVariables_idx <- c(listOfVariables_idx, rep(x = varb, times = length(unique(metaData[[varb]]))))
}
input_mapping <- data.frame(
  listOfValues = listOfValues,
  listOfVariables_idx = listOfVariables_idx
)
listOfTypes <- tdm$Lemma
