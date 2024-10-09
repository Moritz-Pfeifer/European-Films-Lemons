
### The European Film Industry as a (Winner-Take-All) Market for Lemons

This repository contains the code and data for the paper "The European Film Industry as a (Winner-Take-All) Market for Lemons". 

This paper looks at the impact of film criticism on predicting the commercial success of European films. We focus on the EU-funded film journal _Cineuropa_ and compare it against the three largest industry press outlets. Using sentiment analysis to evaluate film reviews and a binary classification algorithm to assess commercial success, we find that _Cineuropa_ has a positive bias. This bias leads the prediction model to overestimate the likelihood of commercial success of films regardless of their actual market performance. We interpret this as evidence that _Cineuropa_ functions more as an advertisement platform than as a source of film criticism, creating misleading signals independent of a film's artistic or commercial merit. This paper makes three contributions: (1) it presents the first predictive study on the European film industry as a whole, (2) it introduces a novel method for classifying commercial success with an emphasis on model explainability, and (3) it adds to empirical research on signaling and asymmetric information.

## Repository Structure

#### 1. [Data](https://github.com/Moritz-Pfeifer/European-Films-Lemons/tree/main/Data)
- This folder contains datasets used for the analysis. 
  - `master0402024.xlsx`: Master file with market data and sentiment scores for European Films
    
  - `master_2022report_24072024.xlsx`: Master file with market data according to the method of the EAO 2023 Report and sentiment scores for European Films
    
  - `classification_24072024.xlsx`: Our admission thresholds for classifying commercial success
    
  - `classification_2022report_24072024.xlsx`: Admission thresholds for classifying commercial success according to the method of the EAO 2023 Report
    
  - `films_withimdb09092024.xlsx`: Market and Festival data for European films retreived from LUMIERE (lumiere.obs.coe.int) and IMDb (imdb.com)
    
  - `moviesOBS09092024.xlsx`: Market data for all European films with theatrical release retreived from LUMIERE (lumiere.obs.coe.int)
    
  - `ticketspercountry2021.xlsx`: Average cinema ticket prices per country

#### 2. [Scrapers](https://github.com/Moritz-Pfeifer/European-Films-Lemons/tree/main/Scrapers)
- This folder contains the scripts for data retrieval. The jupyter notebook ([Scrape_and_Analyse_Market_Data.ipynb](https://github.com/Moritz-Pfeifer/European-Films-Lemons/blob/Scrapers/LUMIERE_and_IMDb_scraper)) includes the code used to retreive data from LUMIERE and IMBb and structurate the market and festival data for classifying commercial success.

#### 3. [Sentiment Analysis](https://github.com/Moritz-Pfeifer/European-Films-Lemons/tree/main/Scrapers)
- The script for analyzing the sentiment of film reviews with [SiEBERT](https://huggingface.co/siebert/sentiment-roberta-large-english) and the script for explaining the sentiment analysis with [Captum](https://github.com/pytorch/captum) and [Layer Integrated Gradients](https://github.com/Moritz-Pfeifer/European-Films-Lemons/blob/main/Layer_Integrated_Gradients). 

#### 4. [Economic Analysis](https://github.com/Moritz-Pfeifer/European-Films-Lemons/blob/main/Master_File.ipynb) 
- The jupyter notebook ([Master_File.ipynb](https://github.com/Moritz-Pfeifer/European-Films-Lemons/blob/main/Master_File.ipynb)) used for the economic analysis including the [XGBoost](https://github.com/dmlc/xgboost) model and [SHAP](https://github.com/shap/shap).  
   

