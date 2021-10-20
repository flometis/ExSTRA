function(input, output, session) {
  output$menuitem <- renderMenu({
    menuItem("Menu item", icon = icon("calendar"))
  })
  
  observe({
    tipoanalisi<-input$tipoanalisi
    valori<-input$valori
    
    choice1 <- listOfVariables
    choice2 <- input_mapping$listOfValues[input_mapping$listOfVariables_idx == input$tipoanalisi]
    choice3 <- listOfTypes

    updateSelectInput(session = session, inputId = "tipoanalisi", choices = choice1, selected = tipoanalisi)
    updateSelectInput(session = session, inputId = "valori", choices = choice2, selected = valori)
    
  })
  
      output$correspondancePlot <- renderPlotly({
        if(input$tipoanalisi == "autore") cadf <- tdm_pivot_author
        if(input$tipoanalisi == "decennio") cadf <- tdm_pivot_decade
        if(input$tipoanalisi == "titolo") cadf <- tdm_pivot_book
        if(input$tipoanalisi == "sesso") cadf <- tdm_pivot_gender
        if(input$tipoanalisi == "anno") cadf <- tdm_pivot_year
        
        if(!is.null(input$types)){
          rowstodelete <- which(cadf$Lemma %in% input$types)
          cadf <- cadf[ -rowstodelete,]
        }
        
        if(!is.null(input$valori)){
          if(length(input$valori)>2){
            lemmas <- cadf$Lemma
            cadf$Lemma <- NULL
            rownames(cadf)<-lemmas
            colstokeep <- which(names(cadf) %in% input$valori)
            cadf <- cadf[,colstokeep]
            cadf <- cadf[apply(cadf,1,sum)>0,]
            cc <- ca(cadf)
            rowcoords <- cc$rowcoord[,1:2]
            rowcoords[,1] <- rowcoords[,1]  + rnorm(nrow(cc$rowcoord),0,0.1)
            rowcoords[,2] <- rowcoords[,2]  + rnorm(nrow(cc$rowcoord),0,0.1)
            fig <- plot_ly(data = as.data.frame(rowcoords), x = rowcoords[,2], y = rowcoords[,1], type = 'scatter',
                           mode = 'text', text = cc$rownames, textposition = 'center',
                           textfont = list(color = '#000000', size = 12))
            fig <- fig %>% add_text(x = cc$colcoord[,2], y = cc$colcoord[,1],
                                    text = cc$colnames, textfont = list(color = '#FF0000', size = 16))
            fig
            
          }
          
        }      
                
      })
      
      output$inertia <- renderPlot({
        if(input$tipoanalisi == "autore") cadf <- tdm_pivot_author
        if(input$tipoanalisi == "decennio") cadf <- tdm_pivot_decade
        if(input$tipoanalisi == "titolo") cadf <- tdm_pivot_book
        if(input$tipoanalisi == "sesso") cadf <- tdm_pivot_gender
        if(input$tipoanalisi == "anno") cadf <- tdm_pivot_year
        
        if(!is.null(input$types)){
          rowstodelete <- which(cadf$Lemma %in% input$types)
          cadf <- cadf[ -rowstodelete,]
        }
        
        if(!is.null(input$valori)){
          if(length(input$valori)>2){
            lemmas <- cadf$Lemma
            cadf$Lemma <- NULL
            rownames(cadf)<-lemmas
            colstokeep <- which(names(cadf) %in% input$valori)
            cadf <- cadf[,colstokeep]
            cadf <- cadf[apply(cadf,1,sum)>0,]
            cc <- ca(cadf)
            barplot(cc$sv)
          }
          
        }     
        })
}

