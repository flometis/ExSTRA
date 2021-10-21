#!/usr/bin/Rscript

#Se lo script viene eseguito da amministratore (permessi di scrittura nella cartella delle librerie), installa le librerie
if (file.access(.libPaths()[1],2)==0) {
    install.packages("ggplot2",repos = "https://cran.stat.unipd.it/");
    install.packages("gridSVG",repos = "https://cran.stat.unipd.it/");
    print("Se ci sono stati errori, esegui sudo apt-get install libxml2-dev e riprova.")
    print("Sembra che tu sia amministratore, sarebbe meglio procedere solo da utente semplice. Vuoi comunque creare i grafici? [y/N]");
    choice <- readLines("stdin", 1);
    if (choice != "Y" && choice != "y") quit();
}

library(ggplot2);
require(gridSVG);


fullpath <- "../../Findings/exstra_dictionary_COMPLETE.csv";


#file <- read.table(fullpath,header=TRUE, sep=",", col.names=c("Lemma" , "Occurrences", "Decade"), colClasses = c("character", "numeric", "factor"));

origfile <- read.table(fullpath,header=TRUE, sep=",");
origsubset <- origfile[, c("Lemma","Occurrences","Decade")] ;
file <- aggregate(. ~Decade+Lemma, data=origsubset, sum, na.rm=TRUE)
#print.data.frame(head(file));

for(i in levels(as.factor(file$Decade))){
    if (i != "") {
        basename <- sub('\\.csv$', '', fullpath);
        basename <- paste(basename,"-", i);
	basename <- basename(basename);

        mytb <- subset(file, file$Decade==i & file$Occurrences!="");
        mytb <- droplevels(mytb);
        
	#Prendo solo le prime 20 professioni
	mytb <- mytb[order(-mytb$Occurrences),]
	mytb <- head(mytb, n=20L)
        #print(mytb);
        #print(levels(mytb));
        
        mytb$Lemma <- factor(mytb$Lemma, levels = mytb$Lemma[order(mytb$Occurrences)])

        # Scrivo i dati per debug
        print(basename)
        #print(mytb);
        # Creo un istogramma
        histogram = ggplot(mytb, aes(x=mytb$Lemma, y=mytb$Occurrences, fill=mytb$Lemma)) + geom_bar(stat="identity");
        # Percentuale o numero puro nelle etichette?
        mylabels = mytb$Occurrences;
        histogram = histogram + stat_count(aes(y=..count..,label=mylabels),geom="text",vjust=-1)
        histogram = histogram + labs(x = NULL, y = NULL, fill = NULL, title = sub('-', ' ', basename));
        histogram = histogram + theme_classic() + theme(axis.line = element_blank(),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        plot.title = element_text(hjust = 0.5, color = "#666666"));

        #Esporto il grafico in un file SVG
        print(histogram);
        grid.export(paste(basename, ".svg", sep=""),addClasses=TRUE);
    }
}


#basename <- sub('\\.csv$', '', fullpath);
#file <- read.table(fullpath,header=TRUE, sep="\t", col.names=c("Lemma" , "Occurrences"), colClasses = c("character", "numeric"));
# Ordino la tabella in base alla prima colonna (i punteggi calcolati con le risposte degli utenti)
#file <- file[order(file$Occurrences),];

#Esporto il grafico in un file SVG
#print(histogram);
#grid.export(paste(basename, ".svg", sep=""),addClasses=TRUE);
