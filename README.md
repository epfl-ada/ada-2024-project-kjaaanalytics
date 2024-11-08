
# Mapping of Global Beer Preferences: A Data-Driven Travel Guide for the Beer Enthusiast

## Abstract
In this project, we’ll assist EPFL student Bob in planning a global, beer-centered trip through data-driven insights. Using geospatial and semantic analysis, we’ll map global beer preferences to help Bob make informed choices.
We’ll analyze beer descriptions by country through natural language processing to uncover unique linguistic patterns and local preferences, enabling Bob to order like a connoisseur. Seasonal variations in beer ratings will be examined to reveal shifts in taste preferences, guiding Bob’s choices based on time of year.
Additionally, a geospatial analysis of beer ratings by U.S. climate zones will identify popular styles in various climates, optimizing Bob’s selections for different regions. Finally, upon his return to EPFL, we’ll leverage these findings to recommend seasonal beer selections for Satellite, EPFL’s student bar, aligned with Swiss climate patterns. This project combines spatial, temporal, and semantic insights to craft an enriched, personalized travel experience for Bob.



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
