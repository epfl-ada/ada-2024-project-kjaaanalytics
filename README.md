# Mapping of Global Beer Preferences: A Data-Driven Travel Guide for the Beer Enthusiast

## Abstract
In this project, the KJAAAnalytics team has taken the challenge of assisting EPFL student Bob in planning a global, beer-centered trip through data-driven insights. Using geospatial and semantic analysis, we’ll map global beer preferences to help Bob make informed choices. We’ll analyze beer descriptions by country through natural language processing to uncover unique linguistic patterns and local preferences, enabling Bob to order like a connoisseur. Seasonal variations in beer ratings will be examined to reveal shifts in taste preferences, guiding Bob’s choices based on time of year. Additionally, a geospatial analysis of beer ratings by U.S. climate zones will identify popular styles in various climates, optimizing Bob’s selections for different regions. Finally, upon his return to EPFL, we’ll leverage these findings to recommend seasonal beer selections for Satellite, EPFL’s student bar, aligned with Swiss climate patterns. 

We invite you to embark on Bob’s journey, discovering fascinating insights and fun facts about global beer preferences. Discover his journey here: https://alex0021.github.io/kjaaanalytics-datastory/



## Research Questions
In this project, we will answer the following questions : 
- What beers have the best ratings depending on the country, or the beer's style ?
- What are the words most used in beer descriptions according to the style of the beer and the user’s country ? 
- What type of beers have the best ratings depending on the climate of the user’s location ?
-	What are the trends in beer preferences according to the seasons ?



## Proposed additional datasets

- Chelsa dataset (use Chelas timeseries at monthly resolution), 30 arcsec resolution, mean temperature and precipitation amount, 1979-2013.
    - *data*: https://chelsa-climate.org/downloads/
    - *technical specifications*: https://chelsa-climate.org/wp-admin/download-page/CHELSA_tech_specification.pdf
    - *data organisation*: Individual .tiff files for each variable and each month, approx size=14.34 GB 
    - *paper*: Karger D.N., Conrad, O., Böhner, J., Kawohl, T., Kreft, H., Soria-Auza, R.W., Zimmermann, N.E, Linder, H.P., Kessler, M. (2018): Data from: Climatologies at high resolution for the earth’s land surface areas. EnviDat. https://doi.org/10.16904/envidat.228.v2.1
- Naturalearth dataset: map dataset for GIS softwares. https://www.naturalearthdata.com/
- *Admin 0* - Countries: map of all countries in the world. https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
    - data organisation: one folder. size=4.7 MB
- *Admin 1* - States, provinces: https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-1-states-provinces/
    - data organisation: one folder. size=889.9 KB



## Methods
### Part 1: Dataset Preprocessing and Statistical Analysis

#### **Main Goal**
- Analyze the data from the "matched" datasets and process the information from various CSV files.

---

#### **Tasks**

1. **Clean Data**:
   - Rename columns with meaningful names.
   - Drop insignificant columns that are out of scope for the project.
   - Check for `NaN` values in the columns across the DataFrames.
   - Convert date formats into readable units (e.g., seconds).

2. **Explore Data**:
   - Examine the shape of the DataFrames.
   - Investigate the types of scores provided.
   - Compare the data between the two websites: Beer Advocate (BA) and Rate Beer (RB).
   - Analyze the distribution of scores across beer styles.
   - Count the number of breweries per country.
   - Visualize the distribution of the four category scores (appearance, aroma, palate, taste) for each beer style.

3. **Group Data**:
   - Merge the DataFrames to create a new DataFrame linking beer name, location, rating score, and overall score.
   - Set a threshold (user-defined) to determine the number of beers scoring above the threshold.
   - Plot the distribution of scores across selected countries.

---

#### **Exploration Questions**
- **Impact of Palate on Ratings**:  
  - How does palate affect the overall rating? Use linear regression or logistic regression to find coefficients.  

- **Statistical Tests**:  
  - Perform statistical tests (Chi-square, ANOVA, etc.) to determine if preferences significantly differ by season or location.  

- **Top 3 Beers Per Country**:  
  - Identify the top 3 beers per country for Bob when he visits specific locations.  

- **Seasonal Ratings Distribution**:  
  - Visualize the distribution of ratings for beers consumed in each season.  
  - Include a violin plot in the storyline to show the seasonal variation.


### Part 2: Analysis of the text reviews with Natural Language Processing (NLP)
Before using reviews for training, it's crucial to preprocess them to remove noise and standardize the text. Below are the common preprocessing steps:

1. **Convert to Lowercase**:  
   - Convert all reviews to lowercase letters to ensure uniformity and treat words with different cases as the same.

2. **Remove Punctuation**:  
   - Remove punctuation marks or special characters, as they do not contribute much to sentiment analysis and can be safely excluded.

3. **Remove Stopwords**:  
   - Eliminate common words like “the,” “is,” “and,” etc., which do not carry significant sentiment and may introduce noise.

4. **Tokenization**:  
   - Split sentences into individual words, allowing for separate analysis of each word and the creation of a word count table.

---

### Split Reviews by Category
- Beers are categorized into 4 groups: **liked**, **neutral**, **disliked**, and **polarizing**.
- These groups are further broken down by country to show differences in wording used in each country for **liked**, **neutral**, **disliked**, and **polarizing** beers. 
  - The 4 groups were defined as follows.
    - **Liked:** 1 standard deviation above the mean 5 star rating.
    - **Disliked:** 1 standard deviation below the mean 5 star rating.
    - **Neutal:** Between Liked and Disliked
    - **Polarizing** Top 10% of rating standard deviations amongst all beers (dynamically set for each country).
---

### Visualization of Key Words
Use **word clouds** and/or **frequency plots** to identify visually and statistically the most common words and phrases for **liked**, **neutral**, **disliked**, and **polarizing** beers overall and in specific countries. 

The **word clouds** act as a visual representation of the word frequency.
The **frequency plots** act as a statistical representation of the word frequency. The word clouds are by default not entirely accurate to the word frequency plots as they prioritize fitting words accurately over sizing words exactly to size based on frequency.


### Part 3: Seasonal and geospatial Analysis
#### **Main Goal**
- Observe general beer preferences trend changes across the geospatial and seasonal dimension.

#### **Importation of Datasets**
- **Chelsea Data**:  
  - Raster data is read using the `rasterio` library.  
  - The resolution of the data is downscaled by a factor of 10 using `torch.nn.AvgPool2d`.  
  - Climatic data is then stored in a `np.array`.  

- **Naturalearth Data**:  
  - Naturalearth's shapefile is read with the `pd.read_csv()` function, which stores the data in a DataFrame.  

---

#### **Visualization of National Beer Preferences on a Map**
- **How**:  
  - Group the DataFrame by `user_country` and merge this DataFrame with the world GeoDataFrame.  
  - Plot each beer preference by selecting the variable of interest when plotting the map of the GeoDataFrame.  
- **Extension**:  
  - This method can be extended and combined with NLP statistics later in the project.  

---

#### **Interpolating Climatic Data Over Country Boundaries**
- **Why**:  
  - To transform raster temperature data, we calculate an average over countries or states of the USA.  
  - This allows comparison of climate and beer preferences.  

- **How**:  
  - Use `rasterio`'s `geometric_mask` to mask the country of interest.  
  - Compute statistics for each region using `np.nanmean`.  

---

#### **Clustering USA datapoints based on monthly mean temperature and precipitation**
- **Why**:  
  - In order to have *n* *typical climates* from which we can derive general beer conclusions
  - To compare Switzerland's climate to the one of the USA's *typical climate* so that a beer style recommendation can be made for Bob.

- **How**:  
  - Using `scipy`'s `KMeans` algorithm with the 12 monthly mean temperature and 12 monthly precipitation values as predictors. The number of clusters *n* is tried for values *n = 2,...,9* and the resulting MSE plotted (this plot can be found either in the notebook or on the website). Based on the MSE plot, *n = 5* is chosen as this point is a good compromise between accuracy and having general enough clusters.
  - The labels are then interpolated per state to allow comparison with beer preferences (as we only have access to the beer preferences by state). The interpolation is made using the mean label per state.
  - Then, to derive beer preferences trends per *typical climate*, we classify the best-rated beer per state. This is done by grouping the beer data per *user_location* (state) and per *beer_style* in the beer dataset filtered to the USA only, and taking the average *rating*. In this step, we only keep *beer_style* where more than 50 reviews are available to ensure statistical robustness of the mean rating. States are then grouped per cluster membership and the favorite *beer_style* of the cluster is obtained through majority voting. 

---

#### **Comparing Climate Between Switzerland and USA States**
- **Why**:  
  - When Bob returns to EPFL, he will recommend beers from a specific beer style based on climate similarity.  

- **How**:  
  - Using the *KMeans* algorithm trained on USA's weather data, we predict Switzerland's classification using its own climatic data (monthly mean temperature and precipitation). We get a cluster label for each data point in Switzerland.
  - We locate Lausanne using its geogaphic coordinates and check for its assigned label. We print the favorite *beer_style* of this cluster in the USA.
  - To recommend specific beers, we find the three globally best-rated (in terms of *rating*) beers in the desired category. To ensure statistical robustness of this step, we keep only the beers with  at least 100 reviews.

---

### Part 4: Funfacts

#### **Funfact 1: Bob travels from Switzerland to UK**

1. **Prepare dataframe**:

- Filter beer rating data for Switzerland and England, compute average ratings by style category for each country, merge the results, and create a pivoted DataFrame to compare ratings, highlighting differences and sorting by the most significant absolute rating differences.

2. **Plot the bar chart using plotly**:

- Generate an interactive Plotly bar chart comparing the 17 beer styles' average ratings between Switzerland and England, annotating significant differences and enhancing chart clarity with a clean design and labels.

- Additionally, a function computes p-values using a t-test to assess the statistical significance of differences in average beer ratings between Switzerland and England for each style category, returning the results as a Series. The significant beer styles are showed with a red star on top.

#### **Funfact 2: Bob travels from UK to Belgium**

1. **Prepare dataframe***:

- Filter Belgian beer data, extract yearly ratings, and identify beers consistently rated across all years, creating datasets for analysis of average ratings by year and beer.

2. **Plot the line chart using plotly**:

- Create a Plotly line chart to visualize year-over-year average ratings for consistently rated Belgian beers, enhancing understanding of trends with markers and a clear, interactive design.

#### **Funfact 3: Bob travels from Belgium to Canada**

1. **Prepare dataframe**:

- Filter beer data for Belgium and Canada, calculate average rating counts by style category, and return datasets for Belgian, and Canadian beer style analysis

2. **Plot the pie charts using plotly**:

- Generate two pie charts using Plotly to compare the distribution of beer styles by rating counts in Belgium and Canada, with distinct color mapping.

#### **Funfact 4: Bob travels from Canada to the USA**

1. **Prepare dataframe**:

- Filter beer data for U.S. breweries, calculate the average rating for each state, and create datasets for analyzing and ranking states by their average beer ratings.
- Identify the most popular brewery in each U.S. state by counting the number of beer entries for each brewery and selecting the one with the highest count per state.

2. **Plot the bar chart using plotly**:

- Generate a bar chart that visualizes the most popular brewery in each U.S. state based on the highest number of entries, with distinct colors for each brewery.


## Proposed timeline
- **15.11.24**: Deadline M2
- **22.11.24**: Homework 2
- **29.11.24**: Homework 2 and Part 1, 2, 3
- **06.12.24**: Final Data Analysis and Part 4, + Begin Working on the Website
- **13.12.24**: Finalize the Data Story Webpage, and use interactive visualizations to show the project
- **20.12.24**: Deadline for the project


## Organization within the team

For Milestone 2: 
- **Kenza and Alex**:  
  Work on Part 1 (Dataset Preprocessing and Statistical Analysis) and Part 4 (Storyline Visualization).  
  - **Kenza**: Focus on the `matched_beer_dataset` i.e., `beers.csv`, `breweries.csv`, `ratings.csv`, and `users_approx.csv`.  
  - **Alex**: Work on the `ratings_with_text.txt` and `users.csv` from both the RB and BA websites.  

- **Amélie and Andrew**:  
  Work on Part 2 (Analysis of the Text Reviews with NLP) and Part 4 (Storyline Visualization).

- **Julie**:  
  Work on Part 3 (Geospatial Analysis) and Part 4 (Storyline Visualization).

For Milestone 3:
- **Amélie and Julie**: Analysis part.

- **Andrew and Alex**: Website implementation.

- **Kenza**: Funfacts part. 


## Quickstart
```bash
# clone project
git clone git@github.com:epfl-ada/ada-2024-project-kjaaanalytics.git
cd ada-2024-project-kjaaanalytics.git

# [OPTIONAL] create virtual environment environment
python -m venv <env_name>
./<env_name>/Scripts/activate

# install requirements
pip install -r pip_requirements.txt

#install Natural Language Tool Kit (NLTK) dependencies
python
>> import nltk
>> nltk.download('stopwords')
>> nltk.download('punkt_tab')

```


### How to use the library
All results are displayed in the jupyter notebook results.ipynb. This notebook calls functions from the folder src/utils. One animation (in the .gif format) can not be displayed properly in the notebook, it is hence additionally saved in the folder output/animation. The folder output will be used in the future to hold more output files.

The `website` folder contains all materials required to generate the visualization of our Data Story. To access the Data Story, the following link can be used: https://alex0021.github.io/kjaaanalytics-datastory/. 



## Project Structure

The directory structure of new project looks like this:

```
├── data                        <- Project data files
│   ├── img                     <- Input images 
│
├── src                         <- Source code
│   ├── data                            <- Data directory
│   ├── models                          <- Model directory
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Shell scripts
│
├── output
│    ├── animations             <- animations 
│
├── tests                       <- Tests of any kind
│
├── results.ipynb               <- a well-structured notebook showing the results
|
├── website                     <- Website related files
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```