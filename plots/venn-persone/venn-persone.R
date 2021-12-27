#!/usr/bin/Rscript
install.packages("VennDiagram",repos = "https://cran.stat.unipd.it/");
require(VennDiagram);
x <- list();
#Mestieri più esercitati da persone nate nel 1820
x$Wiki <- as.character(c( "politico", "pittore", "avvocato", "scrittore", "giornalista", "professore universitario", "ufficiale", "giudice", "medico", "poeta"));
#Mestieri più citati nei romanzi del 1840
x$Findings <- as.character(c( "re", "giudice", "servitore", "medico", "scrittore", "contadino", "barbiere", "mercante", "deputato", "poeta"));
v0 <-venn.diagram(x, lwd = 3, col = c("red", "green"), fill = c("orange", "yellow"), apha = 0.5, filename = NULL, imagetype = "svg");
grid.draw(v0);
overlaps <- calculate.overlap(x);
base <- (length(x)*2);
vl <- 9; #length(v0)
for (i in 1:length(overlaps)){
if (i<base-1) {
v0[[vl-base+i-1]]$label <- paste(setdiff(overlaps[[base-1-i]], overlaps[[base-1]]), collapse = "\n");
} else {
v0[[vl-base+i-1]]$label <- paste(overlaps[[base-1]], collapse = "\n");
}
}
svg(filename = "venn-persone.svg");
grid.newpage();
grid.draw(v0);
