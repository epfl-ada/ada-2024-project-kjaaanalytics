
# A semantic analysis of trends in beer descriptions

## Abstract
Climate is known to affect the culture a lot. In our project we will see if we can observe this climatic influence on culture, via analyzing the semantic used in beers descriptions reviews. To do so, we will:
- combine geospatial analysis and spatial analysis to do a geographical description of the semantic used to describe beers.
- link it with climatic data to find correlations between the 2 variables.

*Problems Julie*:
- culture is a bit too much of a wide concept, how to you differentiate between 2 different cultures, how far away must they be to be different??
- c'est un peu réducteur d'associer tout la culture d'un pays à la description de bières
- jsp si on va pouvoir truver des meaningful conclusions avec l'analyse semantic
- pas tout le dataset est en anglais

v2 : 
Climate is known to affect the mood and overall happiness of people. In our project we will do a sentiment analysis of the overall comments and see how it varies across regions. We will also see if we can observe the climate’s influence, via analyzing the semantic used in beers descriptions reviews and the scores associated. To do so, we will:
•	combine geospatial analysis and spatial analysis to do a geographical description of the semantics used to describe beers.
•	link it with climatic data to find correlations between the 2 variables by looking at different options: 
o	evaluate if there is a link between the bad weather and negatively associated comments and overall scores
o	assess the change in taste preference of users according to the season looking at the overall scores of the different beers.


## Research Questions

## Proposed additional datasets

- Chelsa dataset (use Chelas timeseries at monthly resolution), 30 arcsec resolution, mean temperature and precipitation amount, 1979-2013.
    - *data*: https://chelsa-climate.org/downloads/
    - *technical specifications*: https://chelsa-climate.org/wp-admin/download-page/CHELSA_tech_specification.pdf
    - *data organisation*: Individual .tiff files for each variable and each month, approx size=14.34 GB 
    - *paper*: Karger D.N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R.W., Zimmermann, N.E, Linder, H.P., Kessler, M. (2018): Data from: Climatologies at high resolution for the earth’s land surface areas. EnviDat. https://doi.org/10.16904/envidat.228.v2.1

- WorldClim dataset (use Historical monthly weather data), 2.5 - 10 arcmin resolution (2.5' is approx.20km at the equator), min / max temperature and total precipitation, 1960-2021. 
    - *data*: https://www.worldclim.org/data/monthlywth.html
    - *data organisation*:  Individual .tiff files for each variable and each month, approx size=0.89 GB (for the period 1979-2013 2.5' resolution)
    - *paper*: Fick, S.E. and Hijmans, R.J. (2017), WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas. Int. J. Climatol, 37: 4302-4315. https://doi.org/10.1002/joc.5086


## Methods

## Proposed timeline

## Organization within the team

## Questions for TAs


## Quickstart

```bash
# clone project
git clone git@github.com:epfl-ada/ada-2024-project-kjaaanalytics.git
cd ada-2024-project-kjaaanalytics.git

# [OPTIONAL] create conda environment
conda create -n <env_name> python=3.11 or ...
conda activate <env_name>


# install requirements
pip install -r pip_requirements.txt
```



### How to use the library
Tell us how the code is arranged, any explanations goes here.



## Project Structure

The directory structure of new project looks like this:

```
├── data                        <- Project data files
│
├── src                         <- Source code
│   ├── data                            <- Data directory
│   ├── models                          <- Model directory
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Shell scripts
│
├── tests                       <- Tests of any kind
│
├── results.ipynb               <- a well-structured notebook showing the results
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```

### The README file should have the following structure

- Title
- Abstract: A 150 word description of the project idea and goals. What’s the motivation behind your project? What story would you like to tell, and why?
- Research Questions: A list of research questions you would like to address during the project.
- Proposed additional datasets (if any): List the additional dataset(s) you want to use (if any), and some ideas on how you expect to get, manage, process, and enrich it/them. Show us that you’ve read the docs and some examples, and that you have a clear idea on what to expect. Discuss data size and format if relevant. It is your responsibility to check that what you propose is feasible.
- Methods
- Proposed timeline
- Organization within the team: A list of internal milestones up until project Milestone P3.
- Questions for TAs (optional): Add here any questions you have for us related to the proposed project.