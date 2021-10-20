dashboardPage(
  dashboardHeader(title = "Eltec 100 - Analisi esplorativa dei dati"),
  dashboardSidebar(
    sidebarMenu(
      menuItemOutput("menuitem")
    ),
    selectInput(inputId = "tipoanalisi", label = "Tipo analisi", choices = listOfVariables, selected = "titolo"),
    selectInput(inputId = "valori", label = "Variabili", choices = input_mapping$listOfValues, multiple = TRUE),
    selectInput(inputId = "types", label = "Types da eliminare", choices = listOfTypes, multiple = TRUE)
    
  ),
  dashboardBody(
    fluidRow(
      box(
        plotlyOutput(outputId = "correspondancePlot")
      )),
    fluidRow(  
    box(
        plotOutput(outputId = "inertia")
      )
    )
    
  )
)
  
