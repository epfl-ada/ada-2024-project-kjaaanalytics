import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import nltk
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
import string
import unicodedata
import re
from PIL import Image 

"""
Preprocesses the input text by performing the following steps:
1. Converts the text to a string if it is not already.
2. Removes punctuation.
3. Converts all text to lowercase.
4. Tokenizes the text.
5. Removes stop words.

Parameters:
text (str): The input text to be preprocessed.

Returns:
list: A list of processed tokens after removing stop words.

"""
def preprocess_text(text):
    # Ensure text is a Unicode string
    if isinstance(text, bytes):  # Decode bytes to string if necessary
        text = text.decode('utf-8', errors='replace')
    else:
        text = str(text)  # Ensure text is a string
    
    
    # Normalize to remove accents and special characters
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))  # Remove combining marks

    # Replace common encoding artifacts
    replacements = {
        "â€™": "'", "â€œ": '"', "â€\x9d": '"', "â€“": "-", "â€”": "-", 
        "â€": '"', "â€\x9c": '"', "ã": "a", "â": "a", "©": "e"
    }
    for target, replacement in replacements.items():
        text = text.replace(target, replacement)
    
    # Remove any non-printable or non-ASCII characters
    text = re.sub(r'[^\x20-\x7E]', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    #Convert to lowercase
    text = text.lower()
    
    #Tokenize text
    tokens = word_tokenize(text)
    
    #Remove stop words
    # Define custom stop words
    CUSTOM_STOP_WORDS = {
        "'s", "s", "note", "notes", "almost", "beer", "lots", "quite", "maybe", "lot", 
        "though", "aroma", "flavor", "palate", "overall", "appearance", "n't", "taste", 
        "head", "mouthfeel", "bottle", "glass", "little", "smell", "bit", "one", "lot", 
        "nose", "really", "much", "body", "hint", "quot", "spice", "itas", "good", 
        "great", "nice", "love", "like", "isnt", "isn", "don", "de", "et", "tra", 
        "peu", "garement", "bouche", "bouteille", "verre", "pours", "bia", "bier", 
        "biera", "bire", "pracense"
    }
    stopwords_set = set(stopwords.words('english')).union(CUSTOM_STOP_WORDS)
    stopwords_set_final = set(stopwords.words('french')).union(stopwords_set)
    
    # Filter out stop words
    tokens = [token for token in tokens if token not in stopwords_set_final]
    
    # Join tokens back into a single string
    filtered_text = ' '.join(tokens)
    return filtered_text


"""
Plots a simple word cloud of the input text.

Parameters:
text (list): A list of tokens to be visualized in the word cloud.

Returns:
None -- displays the word cloud plot.
"""
def plot_wordcloud(text):
    beer_mask = np.array(Image.open('data/img/test_2.png'))
    text_single_string = ' '.join(text)
    # Create and generate a word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='viridis',mask=beer_mask, contour_width =2).generate(text_single_string)
    #plt.figure(figsize=(10, 5))
    #plt.imshow(wordcloud, interpolation='bilinear')
    #plt.axis('off')
    return wordcloud.to_array()


"""
Categories the rating of a beer based on the average and standard deviation scores.

Parameters:
avg_score (float): The average score of the beer accross both websites.
std_score (float): The standard deviation score of the beer accross both websites.

Returns:
str: The category of the beer rating.
"""
def categorize_rating(avg_score, std_score, num_ratings, liked_threshold, disliked_threshold, polarizing_threshold, significance=30):
    # Account for NaN and None values
    if pd.isnull(avg_score):
        return 'Unknown'
    if ~pd.isnull(std_score):
        if std_score > polarizing_threshold and num_ratings > significance: #TODO: This num_ratings threshold is arbitrary
            return 'Polarizing' 
        if avg_score >= liked_threshold:
            return 'Liked'
        elif avg_score <= disliked_threshold:
            return 'Disliked'
        elif disliked_threshold < avg_score < liked_threshold:
            return 'Neutral'
        else:
            return 'Unknown'
    else:
        if avg_score >= liked_threshold:
            return 'Liked'
        elif avg_score <= disliked_threshold:
            return 'Disliked'
        elif disliked_threshold < avg_score < liked_threshold:
            return 'Neutral'
        else:
            return 'Unknown'

    
"""
Basic helper function to categorize the rating of a beer:

"""
def apply_rating(row, liked_threshold, disliked_threshold, polarizing_threshold):
    return categorize_rating(row['avg_score'], row['std_score'], row['num_ratings'], liked_threshold, disliked_threshold, polarizing_threshold)

def apply_per_country_rating(row, significance, liked_threshold, disliked_threshold, polarizing_threshold):
    return categorize_rating(row['avg_score_per_country'], row['std_score_per_country'], row['num_ratings_per_country'], liked_threshold, disliked_threshold, polarizing_threshold, significance)
    

"""
This function calculates the categorized ratings for each beer in the dataset 
internal to each country or US state.

Parameters:
df (pd.DataFrame): The input DataFrame containing the beer data with country information stored in the "location_user" column.

Returns:
pd.DataFrame: A DataFrame containing the categorized ratings for each beer in the dataset
internal to each country or US state.


"""
def calculate_ratings_by_country(df, significance, liked_threshold, disliked_threshold):
    column_name = 'location_user'

    # Ensure df is a DataFrame and column_name exists in df
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The input df is not a pandas DataFrame.")
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist in the DataFrame.")

    # Get the unique countries of the location_user column
    countries = df[column_name].unique()

    # Initialize new columns in the DataFrame
    df['avg_score_per_country'] = 0.0
    df['std_score_per_country'] = 0.0
    df['num_ratings_per_country'] = 0.0
    df['rating_label_per_country'] = None

    for country in countries:
        # Filter the data for each country
        country_data = df[df[column_name] == country]

        # Calculate the average and standard deviation scores for each beer in the country
        country_data.loc[:,'avg_score_per_country'] = country_data.groupby('beer_name')['rating'].transform('mean')
        country_data.loc[:,'std_score_per_country'] = country_data.groupby('beer_name')['rating'].transform('std')
        country_data.loc[:,'num_ratings_per_country'] = country_data.groupby('beer_name')['rating'].transform('count')

        # Calculate the 90th percentile of the standard deviation scores for each country
        polarizing_threshold = country_data['std_score_per_country'].quantile(0.9)

        # Categorize the rating of each beer in the country
        country_data.loc[:,'rating_label_per_country'] = country_data.apply(apply_per_country_rating, axis=1, args=(significance, liked_threshold, disliked_threshold, polarizing_threshold))

        # country_data['rating_label_per_country'] = country_data.apply(apply_per_country_rating, axis=1)

        # Update all the rows in the original data frame with the rows in the country data
        
        # List of columns to update
        update_columns = ['avg_score_per_country', 'std_score_per_country', 'num_ratings_per_country', 'rating_label_per_country']

        # Update the original DataFrame with the country data
        df.loc[country_data.index, update_columns] = country_data[update_columns]
    
    return df

# Define a function to plot the word cloud and word frequency graphs for a given country for each of the 4 labels of liked, neutral, disliked, and polarizing
def plot_country_wordclouds(df, country):
    country_data = df[df['location_user'] == country]
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))

    for i, label in enumerate(['Liked', 'Neutral', 'Disliked', 'Polarizing']):
        label_data = country_data[country_data['rating_label_per_country'] == label]
        label_text = ' '.join(label_data['preprocessed text'])
        
        # Generate word cloud
        wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='viridis').generate(label_text)
        
        # Plot word cloud
        axes[0, i].imshow(wordcloud, interpolation='bilinear')
        axes[0, i].set_title(f'Word Cloud for {label} Beers in {country}')
        axes[0, i].axis('off')
        
        # Plot histogram
        words = label_text.split()
        word_freq = pd.Series(words).value_counts().head(20)
        word_freq.plot(kind='bar', ax=axes[1, i])
        axes[1, i].set_title(f'Word Frequency for {label} Beers in {country}')
        axes[1, i].set_xlabel('Words')
        axes[1, i].set_ylabel('Frequency')

    plt.show()