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
import plotly.express as px
from plotly.io import write_html
from src.utils.data_utils import get_beer_style_mapping
from src.utils.geospatial_utils import get_season
import seaborn as sns


def preprocess_text(text):
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




def generate_wordcloud(text, saving_path, name_beer, mask_path='data/img/image_beers.png', dpi=600, figsize=(15, 7.5)):
    """
    Generate and save a word cloud image without plotting it.
    
    Parameters:
    - text (list of str): List of words for the word cloud.
    - saving_path (str): Path to save the generated word cloud image.
    - name_beer (str): Name of the beer for the title.
    - mask_path (str, optional): Path to the image mask. Defaults to 'data/img/image_beers.png'.
    - dpi (int, optional): Resolution of the saved image. Defaults to 600.
    - figsize (tuple, optional): Size of the figure in inches. Defaults to (15, 7.5).

    Returns:
    None -- displays the word cloud plot.
    """
    beer_mask = np.array(Image.open('data/img/image_beers.png'))

    # Combine text into a single string
    text_single_string = ' '.join(text)

    # Generate the word cloud
    wordcloud = WordCloud(
        width=800, height=400, background_color='white',
        colormap='viridis', mask=beer_mask, contour_width=2
    ).generate(text_single_string)

    # Create a figure without displaying it
    fig = plt.figure(figsize=figsize)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title('Word Cloud for ' + name_beer)
    plt.axis('off')

    # Save the figure
    fig.savefig(saving_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)  # Close the figure to save memory



def categorize_rating(avg_score, std_score, num_ratings, liked_threshold, disliked_threshold, polarizing_threshold, significance=30):
    """
    Categories the rating of a beer based on the average and standard deviation scores.

    Parameters:
    avg_score (float): The average score of the beer accross both websites.
    std_score (float): The standard deviation score of the beer accross both websites.

    Returns:
    str: The category of the beer rating.
    """
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

    

def apply_rating(row, liked_threshold, disliked_threshold, polarizing_threshold):
    """
    Basic helper function to categorize the rating of a beer:

    """
    return categorize_rating(row['avg_score'], row['std_score'], row['num_ratings'], liked_threshold, disliked_threshold, polarizing_threshold)

def apply_per_country_rating(row, significance, liked_threshold, disliked_threshold, polarizing_threshold):
    return categorize_rating(row['avg_score_per_country'], row['std_score_per_country'], row['num_ratings_per_country'], liked_threshold, disliked_threshold, polarizing_threshold, significance)
    


def calculate_ratings_by_country(df, significance, liked_threshold, disliked_threshold):
    """
    This function calculates the categorized ratings for each beer in the dataset 
    internal to each country or US state.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the beer data with country information stored in the "location_user" column.

    Returns:
    pd.DataFrame: A DataFrame containing the categorized ratings for each beer in the dataset
    internal to each country or US state.


    """
    column_name = 'location_user'

    # Ensure df is a DataFrame and column_name exists in df
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The input df is not a pandas DataFrame.")
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist in the DataFrame.")

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

def plot_beer_mapping(output_folder_html="website/_layouts/"):
    """Plots the sunburst diagram of the beer mapping"""
    style_mapping = get_beer_style_mapping()
    data = pd.DataFrame(list(style_mapping.items()), columns=['Beer Style', 'Category'])
    fig = px.sunburst(
    data,
    path=['Category', 'Beer Style'],  # Hierarchy: Category > Beer Style
    values=None,  
    color='Category',  
    )
    fig.update_traces(
    hovertemplate='<b>%{label}</b><br>Category: %{parent}',
    ) 

    # Customize layout
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25),paper_bgcolor="rgb(0,0,0, 0)")
    output_file = "interactive_beer_mapping.html"
    write_html(fig, file=output_folder_html+output_file, full_html=True)
    fig.show()


def generate_wordcloud_country(df,country='England'): 
    """This function generates word clouds for all the different beer styles
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the beer data with country information stored in the "location_user" column.
    country : the country we want to plot the wordclouds for 
    """
    df_country=df[df['country_user']==country]
    # Create word clouds for all beer styles and store their image arrays
    styles = df_country['style_category'].unique()
    styles = styles[styles != 'Other']
    output_folder_figures = "website/assets/figures/wordcloud_categories/"

    wordcloud_images = {}
    for style in styles:
        path=output_folder_figures+style+'.svg'
        text = df_country[df_country['style_category'] == style]['preprocessed text']
        wordcloud_images[style] = generate_wordcloud(text,path,style)


def plot_radar_chart(df, country, rating_label, categories):
    """
    Generates a radar chart for the top 5 polarizing beers in a given country.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input data containing beer information with the necessary attributes such as 
        aroma, palate, taste, appearance, and average scores.
        
    country : str
        The country for which the top polarizing beers will be plotted.
        
    rating_label : str
        The label used to filter beers based on their rating classification 
        
    categories : list of str
        The attributes (columns) to include in the radar chart, such as 
        ['aroma', 'palate', 'taste', 'appearance', 'avg_score_per_country'].
    """
    saving_path="website/assets/figures/Top_5_Polarizing_Beers_in_Canada.svg"
    df_filtered = df[(df['country_user'] == country) & (df['rating_label_per_country'] == rating_label)]
    df_filtered['beer_names_count'] = df_filtered['beer_name']
    top_beers = df_filtered.groupby('beer_name').agg({
        'aroma': 'mean',
        'palate': 'mean',
        'taste': 'mean',
        'appearance': 'mean',
        'avg_score_per_country': 'mean',
        'std_score_per_country': 'mean', 'beer_names_count':'count'
    }).reset_index()
    
    top_beers = top_beers[top_beers['beer_names_count']>10] #filter beers with more than 10 ratings
    # Sort and select the top 5 beers, by best average per sountry
    top_beers = top_beers.sort_values(by='avg_score_per_country').head(5)

    
    num_vars = len(categories)

    
    colors = sns.color_palette('viridis', len(top_beers))

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1] 

    # Add radar plots
    for i, beer in enumerate(top_beers.itertuples()):
        values = list(getattr(beer, cat) for cat in categories)  
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=beer.beer_name, color=colors[i])
        ax.fill(angles, values, alpha=0.15, color=colors[i])
    categories=['Taste','Aroma','Appearance','Average score','Palate']
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_yticklabels([])
    fig.suptitle(f'Top 5 Polarizing Beers in {country}', fontsize=16, ha='center', va='top', y=0.95)
    plt.legend(loc='lower right', bbox_to_anchor=(1.3, -0.1), frameon=False)

    plt.tight_layout()
    plt.show()
    fig.savefig(saving_path,format='svg', bbox_inches='tight')





def plot_combined_distribution(df, one_sigma, minus_one_sigma,country='Canada'):
    """
    Combines the overall rating distribution and standard deviation distribution plots into subplots.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing beer data.
    country : str, optional
        The country for which the plots will be generated (default is 'Canada').
    one_sigma : float, optional
        The threshold for "liked" ratings (default is None).
    minus_one_sigma : float, optional
        The threshold for "disliked" ratings (default is None).
    """
    output_folder_svg = "website/assets/figures/"
    
    # Calculate the polarizing threshold for the standard deviation
    too_high_std = df['std_score_per_country'].quantile(0.9)
    df_country = df[df['country_user'] == country]
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 6))
    
    # Plot 1: Overall Rating Distribution
    df_country['rating'].astype(float).plot(
        kind='hist', bins=20, ax=axes[0], color='purple', edgecolor='black', alpha=0.7
    )
    axes[0].set_title('Overall Distribution of Beer Ratings in ' + country, fontsize=14)
    axes[0].set_xlabel('Rating', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].axvline(one_sigma, color='magenta', linestyle='--', label='Liked threshold')
    axes[0].axvline(minus_one_sigma, color='skyblue', linestyle='--', label='Disliked threshold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, linestyle='--', alpha=0.6)
    
    # Plot 2: Standard Deviation Distribution
    df_country['std_score_per_country'].plot(
        kind='hist', bins=30, ax=axes[1], color='purple', edgecolor='black', alpha=0.7
    )
    axes[1].axvline(too_high_std, color='red', linestyle='--', linewidth=2, label='Polarizing threshold')
    axes[1].set_title('Standard Deviation Distribution of Ratings for ' + country, fontsize=14)
    axes[1].set_xlabel('Standard Deviation', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, linestyle='--', alpha=0.6)
    
    # Adjust layout and save the figure
    plt.tight_layout()
    fig.savefig(output_folder_svg + country.lower().replace(" ", "_") + '_beer_distributions.svg', format='svg')
    plt.show()


def generate_wordclouds(df,seasonal=True,  mask_path='data/img/image_beers.png', dpi=1200, figsize=(15, 7.5)):
    """
    Generate and save word cloud images for each season without plotting them.
    
    Parameters:
    - df (DataFrame): DataFrame containing the data.
    - country (str): Name of the country for the title.
    - mask_path (str, optional): Path to the image mask. Defaults to 'data/img/image_beers.png'.
    - dpi (int, optional): Resolution of the saved image. Defaults to 600.
    - figsize (tuple, optional): Size of the figure in inches. Defaults to (15, 7.5).

    Returns:
    plots the wordcloud and saves the word cloud images.
    """
    beer_mask = np.array(Image.open(mask_path))
    if seasonal:
        saving_path="website/assets/figures/word_clouds_seasons.svg"
        seasons = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
        fig, axs = plt.subplots(2, 2)
        axs = axs.flatten()
        
        for i, (season_num, season_name) in enumerate(seasons.items()):
            season_df = df[df['season_num'] == season_num]
            text = ' '.join(season_df['preprocessed text'].tolist())
            wordcloud = WordCloud(background_color='white', mask=beer_mask, contour_width=2).generate(text)
            
            axs[i].imshow(wordcloud, interpolation='bilinear')
            axs[i].set_title(f'{season_name}')
            axs[i].axis('off')
            plt.tight_layout(pad=2.0, w_pad=1.5, h_pad=1.5)  # Reduce the space between subplots
            plt.show()
            plt.savefig(saving_path, dpi=dpi, bbox_inches='tight')
    else:
        fig = plt.figure(figsize=(10, 5)) 
        text = ' '.join(df['preprocessed text'].tolist())
        wordcloud = WordCloud(background_color='white', mask=beer_mask, contour_width=2).generate(text)
        plt.tight_layout(pad=2.0, w_pad=1.5, h_pad=1.5)  # Reduce the space between subplots
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title('Wordcloud for Stout styles beers')
        plt.axis('off')
        plt.tight_layout(pad=2.0)
        plt.show()


    