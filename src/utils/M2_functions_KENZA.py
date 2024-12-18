#Imports
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import interactive
from ipywidgets import IntSlider



### 1/ beers.csv files

def preprocess_beers_df(beers_df):
    """
    Preprocesses the input beer DataFrame by renaming columns, removing the first row, resetting the index, 
    and dropping unnecessary columns.

    Parameters:
    ----------
    beers_df (pandas.DataFrame): The input beer data.

    Returns:
    ----------
    beers_df_copy (pandas.DataFrame): A cleaned and processed version of the input DataFrame.
    """
    # Making a copy of the beers_df, rename the column names and remove the first row indexed with 0 since it is now merged in the column names
    beers_df_copy=beers_df.copy()
    beers_df_copy= beers_df_copy.rename(columns={'ba': 'ba_abv', 'ba.1': 'ba_avg', 'ba.2': 'ba_avg_computed', 'ba.3': 'ba_avg_matched_valid_ratings', 'ba.4': 'ba_score', 
                                                'ba.5': 'ba_beer_id', 'ba.6': 'ba_beer_name', 'ba.7': 'ba_beer_wout_brewery_name','ba.8':'ba_brewery_id',
                                                'ba.9': 'ba_brewery_name','ba.10': 'ba_bros_score', 'ba.11': 'ba_nbr_matched_valid_ratings', 'ba.12': 'ba_nbr_ratings', 
                                                'ba.13': 'ba_nbr_reviews', 'ba.14': 'ba_style', 'ba.15': 'ba_zscore', 
                                                'rb': 'rb_abv','rb.1': 'rb_avg', 'rb.2': 'rb_avg_computed', 'rb.3': 'rb_avg_matched_valid_ratings', 'rb.4': 'rb_beer_id', 
                                                'rb.5': 'rb_beer_name', 'rb.6': 'rb_beer_wout_brewery_name', 'rb.7': 'rb_brewery_id', 'rb.8': 'rb_brewery_name', 
                                                'rb.9': 'rb_nbr_matched_valid_ratings', 'rb.10': 'rb_nbr_ratings', 'rb.11': 'rb_overall_score', 'rb.12': 'rb_style', 
                                                'rb.13': 'rb_style_score', 'rb.14': 'rb_zscore', 'scores': 'scores_diff', 'scores.1': 'scores_sim'}) 
    beers_df_copy = beers_df_copy.drop(index=0)
    beers_df_copy = beers_df_copy.reset_index(drop=True)

    # Removing some columns that are not relevant for the scope of our project
    beers_df_copy= beers_df_copy.drop(columns=['ba_avg_computed', 'ba_beer_id', 'ba_beer_wout_brewery_name',
                                                'ba_brewery_id', 'rb_avg_computed', 'rb_beer_id', 'scores_diff', 'scores_sim'])
    
    return beers_df_copy


def prepare_df_beers(beers_df_copy):
    """
    Reshapes and cleans the beer data to include style, score, and source (BA or RB).

    Filters out styles that don't have scores from both 'BA' and 'RB'.

    Parameters:
    ----------
    beers_df_copy (pandas.DataFrame): The input beer data.

    Returns:
    ----------
    beers_subset_df (pandas.DataFrame): A cleaned DataFrame with styles having scores from both 'BA' and 'RB'.
    """
    # Making a new dataframe with columns style, score and source (ba or rb)
    beers_subset_df= pd.melt(beers_df_copy[['ba_score', 'ba_style', 'rb_overall_score', 'rb_style']], 
                        id_vars=['ba_style', 'rb_style'], 
                        value_vars=['ba_score', 'rb_overall_score'],
                        var_name='source', 
                        value_name='score')
    beers_subset_df['source'] = beers_subset_df['source'].replace({'ba_score': 'BA', 'rb_overall_score': 'RB'})
    beers_subset_df['style'] = beers_subset_df.apply(lambda row: row['ba_style'] if row['source'] == 'BA' else row['rb_style'], axis=1)
    beers_subset_df = beers_subset_df.drop(columns=['ba_style', 'rb_style'])
    beers_subset_df['score'] = pd.to_numeric(beers_subset_df['score'], errors='coerce')
    beers_subset_df = beers_subset_df.dropna()
    beers_subset_df = beers_subset_df.reset_index()

    # Grouping by style and check if each style has both 'BA' and 'RB' sources and filter to keep only styles that have scores from both 'BA' and 'RB'
    styles_with_both_sources = beers_subset_df.groupby('style')['source'].nunique() == 2
    beers_subset_df = beers_subset_df[beers_subset_df['style'].isin(styles_with_both_sources[styles_with_both_sources].index)]
    return beers_subset_df


def plot_df_beers(beers_subset_df,num_styles,unique_styles,):
    """
    Plots boxplots of beer scores by style and source (BA or RB).

    Parameters:
    ----------
    beers_subset_df (pandas.DataFrame): The DataFrame containing beer data.
    num_styles (int): The number of unique styles to plot.
    unique_styles (list): A list of unique beer styles.

    Returns:
    ----------
    None: Displays the plots.
    """
    ncols = 5
    nrows = int(np.ceil(num_styles / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows), sharey=True)
    axes = axes.flatten()
    for i, style in enumerate(unique_styles):
        sns.boxplot(data=beers_subset_df.loc[beers_subset_df['style'] == style], x='source', y='score', ax=axes[i])
        axes[i].set_title(f"Style: {style}")
        axes[i].set_xlabel("Source")
        axes[i].set_ylabel("Score")

    # Hiding any unused axes if num_styles is less than total subplot slots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Distribution of BA and RB Scores by Style", y=1)
    plt.tight_layout()
    plt.show()


### 2/ breweries.csv files
def preprocess_breweries_df(breweries_df):
    """
    Preprocesses the input breweries DataFrame by renaming columns, removing the first row, 
    resetting the index, and dropping unnecessary columns.

    Parameters:
    ----------
    breweries_df (pandas.DataFrame): The input breweries data.

    Returns:
    ----------
    breweries_df_copy (pandas.DataFrame): A cleaned version of the input breweries DataFrame.
    """
    # Making a copy of the breweries_df, rename the column names and remove the first row indexed with 0 since it is now merged in the column names
    breweries_df_copy=breweries_df.copy()
    breweries_df_copy= breweries_df_copy.rename(columns={'ba': 'ba_brewery_id', 'ba.1': 'ba_location', 'ba.2': 'ba_brewery_name', 'ba.3': 'ba_nbr_beers', 
                                                'rb': 'rb_brewery_id','rb.1': 'rb_location', 'rb.2': 'rb_brewery_name', 'rb.3': 'rb_nbr_beers', 'scores': 'scores_diff', 'scores.1': 'scores_sim'}) 
    breweries_df_copy = breweries_df_copy.drop(index=0)
    breweries_df_copy = breweries_df_copy.reset_index(drop=True)

    # Removing some columns that are not relevant for the scope of our project
    breweries_df_copy= breweries_df_copy.drop(columns=['ba_brewery_id', 'rb_brewery_id', 'scores_diff', 'scores_sim'])
    return breweries_df_copy


def prepare_df_breweries(breweries_df_copy):
    """
    Prepares a DataFrame with the count of breweries by location for both BA and RB sources.

    Parameters:
    ----------
    breweries_df_copy (pandas.DataFrame): The input breweries data.

    Returns:
    --------
    result_df (pandas.DataFrame) : A DataFrame with brewery counts by location for both BA and RB sources.
    """
    # Grouping by ba_location and count breweries
    ba_counts = breweries_df_copy.groupby('ba_location')['ba_brewery_name'].count().reset_index()
    ba_counts.columns = ['location', 'number_of_breweries_per_location_ba']

    # Grouping by rb_location and count breweries  
    rb_counts =breweries_df_copy.groupby('rb_location')['rb_brewery_name'].count().reset_index()
    rb_counts.columns = ['location', 'number_of_breweries_per_location_rb']

    # Combining the results of both ba and rb
    result_df = pd.merge(ba_counts, rb_counts, on='location')
    result_df = result_df.sort_values(by='number_of_breweries_per_location_ba', ascending=False)
    return result_df

##Function to plot the number of breweries per location
def plot_df_breweries(result_df, n):
    """
    Plots the number of breweries per location (BA vs RB) for the top N locations.

    Parameters:
    ----------
    result_df (pandas.DataFrame): DataFrame containing the brewery counts per location for BA and RB sources.
    n (int): The number of top locations to plot.

    Returns:
    ---------
    None: Displays the bar plot.
    """
    # Select top N locations
    top_result_df = result_df.nlargest(n, 'number_of_breweries_per_location_ba')

    # Plotting
    x = np.arange(len(top_result_df))
    width = 0.2
    plt.figure(figsize=(10, 10))
    plt.bar(x - width/2, top_result_df['number_of_breweries_per_location_ba'], width, label='BA website')
    plt.bar(x + width/2, top_result_df['number_of_breweries_per_location_rb'], width, label='RB website')
    plt.yscale('log')
    plt.title(f'Number of Breweries per Location (Top {n} Countries)')
    plt.xlabel('Location (Country)')
    plt.ylabel('Number of Breweries (Log Scale)')
    plt.xticks(x, top_result_df['location'], rotation=45, ha='right', fontsize=10)
    plt.legend()
    plt.tight_layout()
    plt.show()


### 3/ ratings.csv files
def preprocess_ratings_df(ratings_df):
    """
    Preprocesses the input ratings DataFrame by renaming columns, removing unnecessary rows and columns, 
    and converting date columns to readable formats.

    Parameters:
    ----------
    ratings_df (pandas.DataFrame): The input ratings data.

    Returns:
    --------
    ratings_df_copy (pandas.DataFrame): A cleaned version of the input ratings DataFrame with renamed columns and date columns converted.
    """
    # Making a copy of the ratings_df, rename the column names and remove the first row indexed with 0 since it is now merged in the column names
    ratings_df_copy=ratings_df.copy()
    ratings_df_copy= ratings_df_copy.rename(columns={'ba': 'ba_abv', 'ba.1': 'ba_appearance', 'ba.2': 'ba_aroma', 'ba.3': 'ba_beer_id', 'ba.4': 'ba_beer_name', 
                                                    'ba.5': 'ba_brewery_id', 'ba.6': 'ba_brewery_name', 'ba.7': 'ba_date', 'ba.8': 'ba_overall', 'ba.9': 'ba_palate',
                                                    'ba.10': 'ba_rating', 'ba.11': 'ba_review', 'ba.12': 'ba_style', 'ba.13': 'ba_taste', 'ba.14': 'ba_text', 
                                                    'ba.15': 'ba_user_id', 'ba.16': 'ba_user_name', 'rb': 'rb_abv', 'rb.1': 'rb_appearance', 'rb.2': 'rb_aroma', 
                                                    'rb.3': 'rb_beer_id', 'rb.4': 'rb_beer_name', 'rb.5': 'rb_brewery_id', 'rb.6': 'rb_brewery_name', 'rb.7': 'rb_date', 
                                                    'rb.8': 'rb_overall', 'rb.9': 'rb_palate', 'rb.10': 'rb_rating', 'rb.11': 'rb_style', 'rb.12': 'rb_taste', 'rb.13': 'rb_text', 
                                                    'rb.14': 'rb_user_id', 'rb.15': 'rb_user_name'}) 
    ratings_df_copy = ratings_df_copy.drop(index=0)
    ratings_df_copy = ratings_df_copy.reset_index(drop=True)

    # Removing some columns that are not relevant for the scope of our project
    ratings_df_copy= ratings_df_copy.drop(columns=['ba_beer_id', 'ba_brewery_id', 'ba_user_id', 'rb_beer_id', 'rb_brewery_id', 'rb_user_id'])

    # Converting the date columns of both ba and rb to readable dates
    ratings_df_copy['ba_date'] = pd.to_datetime(pd.to_numeric(ratings_df_copy['ba_date'], errors='coerce'), unit='s')
    ratings_df_copy['rb_date'] = pd.to_datetime(pd.to_numeric(ratings_df_copy['rb_date'],errors='coerce'), unit='s')
    return ratings_df_copy

def prepare_df_ratings_ba(ratings_df_copy):
    """
    Prepares the ratings DataFrame for the BA website by cleaning and reshaping the data.

    Parameters:
    ----------
    ratings_df_copy (pandas.DataFrame): The input ratings data for the BA website.

    Returns:
    --------
    tuple: A tuple containing two DataFrames:
        - ratings_df_copy_nonan_ba : A cleaned DataFrame with relevant ratings for BA.
        - ratings_df_copy_nonan_subset_ba : A reshaped DataFrame with 'style', 'category', and 'score' columns for BA ratings.
    """
    # Filtering out rows with NaN values in relevant columns for RB website 
    ratings_df_copy_nonan_ba = ratings_df_copy.dropna(subset=['ba_appearance', 'ba_aroma', 'ba_palate', 'ba_taste'])
    ratings_df_copy_nonan_ba =ratings_df_copy_nonan_ba .rename(columns={'ba_style': 'style'})

    # Modifying the DataFrame to have one column for the style, one for the category (appearance, aroma, etc.) and one for the score
    ratings_df_copy_nonan_subset_ba = ratings_df_copy_nonan_ba .melt(id_vars=['style'], 
                                value_vars=['ba_appearance', 'ba_aroma', 'rb_palate', 'ba_taste'], 
                                var_name='category', 
                                value_name='score')
    ratings_df_copy_nonan_subset_ba['score'] = pd.to_numeric(ratings_df_copy_nonan_subset_ba['score'], errors='coerce')
    ratings_df_copy_nonan_subset_ba['category'] = ratings_df_copy_nonan_subset_ba['category'].str.replace('ba_', '', regex=False)

    ratings_df_copy_nonan_ba=ratings_df_copy_nonan_ba.rename(columns={'style': 'ba_style'})
    return ratings_df_copy_nonan_ba, ratings_df_copy_nonan_subset_ba

def prepare_df_ratings_rb(ratings_df_copy):
    """
    Prepares the ratings DataFrame for the RB website by cleaning and reshaping the data.

    Parameters:
    ----------
    ratings_df_copy (pandas.DataFrame): The input ratings data for the RB website.

    Returns:
    ----------
    tuple: A tuple containing two DataFrames:
        - ratings_df_copy_nonan_rb : A cleaned DataFrame with relevant ratings for RB.
        - ratings_df_copy_nonan_subset_rb : A reshaped DataFrame with 'style', 'category', and 'score' columns for RB ratings.
    """
    # Filtering out rows with NaN values in relevant columns for RB website 
    ratings_df_copy_nonan_rb = ratings_df_copy.dropna(subset=['rb_appearance', 'rb_aroma', 'rb_palate', 'rb_taste'])
    ratings_df_copy_nonan_rb=ratings_df_copy_nonan_rb.rename(columns={'rb_style': 'style'})

    # Modifying the DataFrame to have one column for the style, one for the category (appearance, aroma, etc.) and one for the score
    ratings_df_copy_nonan_subset_rb = ratings_df_copy_nonan_rb.melt(id_vars=['style'], 
                                value_vars=['rb_appearance', 'rb_aroma', 'rb_palate', 'rb_taste'], 
                                var_name='category', 
                                value_name='score')

    ratings_df_copy_nonan_subset_rb['score'] = pd.to_numeric(ratings_df_copy_nonan_subset_rb['score'], errors='coerce')
    ratings_df_copy_nonan_subset_rb['category'] = ratings_df_copy_nonan_subset_rb['category'].str.replace('rb_', '', regex=False)

    ratings_df_copy_nonan_rb=ratings_df_copy_nonan_rb.rename(columns={'style': 'rb_style'})
    return ratings_df_copy_nonan_rb,ratings_df_copy_nonan_subset_rb

##Function to plot the boxplots for a selected number of styles
def plot_df_ratings(ratings_df_copy_nonan_subset, num_styles, website):
    """
    Plots the distribution of ratings (appearance, aroma, palate, taste) for the top `num_styles`.

    Parameters:
    ----------
    ratings_df_copy_nonan_subset (pandas.DataFrame): The ratings data with style, category, and score.
    num_styles (int): The number of top styles to plot.
    website (str): The website name (e.g., 'BA' or 'RB') to display in the plot title.

    Returns:
    ----------
    None: Displays the boxplots for the selected styles.
    """
    # Getting the top `num_styles`
    selected_styles = ratings_df_copy_nonan_subset['style'].unique()[:num_styles]
    df_selected_styles = ratings_df_copy_nonan_subset[ratings_df_copy_nonan_subset['style'].isin(selected_styles)]

    #Plotting
    fig, axes = plt.subplots(num_styles, 1, figsize=(10, num_styles * 4), sharex=True)
    for i, (style, group_data) in enumerate(df_selected_styles.groupby('style')):
        sns.boxplot(data=group_data, x='category', y='score', ax=axes[i], hue='category')
        axes[i].set_title(f"Distribution of Appearance, Aroma, Palate, and Taste Scores for Style: {style}")
        axes[i].set_xlabel("")
        axes[i].set_ylabel("Score")
        #axes[i].legend(title='Categories', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.suptitle(f"Distribution of Scores by Style for {website}", y=1)
    plt.tight_layout()
    plt.show()


### 4/ users_approx.csv files
def preprocess_users_approx_df(users_approx_df):
    """
    Preprocesses the input users' approximate data by renaming columns, removing irrelevant rows and columns.

    This function renames columns for clarity, removes the first row, resets the index, and drops columns 
    that are not necessary for further analysis.

    Parameters:
    ----------
    users_approx_df (pandas.DataFrame): The input DataFrame containing user data for both BA and RB.

    Returns:
    --------
    users_approx_df_copy (pandas.DataFrame): A cleaned version of the input DataFrame with relevant user data.
    """
    # Making a copy of the users_approx_df, rename the column names and remove the first row indexed with 0 since it is now merged in the column names
    users_approx_df_copy=users_approx_df.copy()
    users_approx_df_copy= users_approx_df_copy.rename(columns={'ba': 'ba_joined_date', 'ba.1': 'ba_location', 'ba.2': 'ba_nbr_ratings', 'ba.3': 'ba_nbr_reviews', 'ba.4': 'ba_user_id',
                                                                'ba.5': 'ba_user_name', 'ba.6': 'ba_user_name_lower', 'rb': 'rb_joined_date', 'rb.1': 'rb_location',
                                                                'rb.2': 'rb_nbr_ratings', 'rb.3': 'rb_user_id', 'rb.4': 'rb_user_name', 'rb.5': 'rb_user_name_lower', 'scores': 'rb_sim'}) 
    users_approx_df_copy = users_approx_df_copy.drop(index=0)
    users_approx_df_copy = users_approx_df_copy.reset_index(drop=True)

    # Removing some columns that are not relevant for the scope of our project
    users_approx_df_copy= users_approx_df_copy.drop(columns=['ba_joined_date', 'ba_user_name', 'ba_user_id', 'rb_joined_date' ,'rb_user_name', 'rb_user_id', 'rb_sim'])

    return users_approx_df_copy


### 5/ Merged dataframe from all four csv files above
def preprocess_final_ba(beers_df_copy, breweries_df_copy, ratings_df_copy_nonan_ba):
    """
    Merges beer, brewery, and ratings data for the BA website. Combines relevant columns from the beers, breweries, and ratings DataFrames into a final DataFrame 
    with beer names, brewery names, locations, and ratings.

    Parameters:
    ----------
    beers_df_copy (pandas.DataFrame): Beer data for the BA website.
    breweries_df_copy (pandas.DataFrame): Brewery data for the BA website.
    ratings_df_copy_nonan_ba (pandas.DataFrame): Ratings data for the BA website.

    Returns:
    --------
    final_df_ba (pandas.DataFrame): Final merged DataFrame with beer and brewery information and ratings.
    """
    # Merging beers.csv and breweries.csv on 'ba_brewery_name' to add 'ba_location' to beers.csv for BA website 
    df_ba_subset = beers_df_copy[['ba_abv', 'ba_avg', 'ba_avg_matched_valid_ratings',
                                'ba_score', 'ba_beer_name', 'ba_brewery_name', 'ba_bros_score',
                                'ba_nbr_matched_valid_ratings', 'ba_nbr_ratings', 'ba_nbr_reviews',
                                'ba_style', 'ba_zscore']]
    merged_df1 = pd.merge(df_ba_subset, breweries_df_copy[['ba_brewery_name', 'ba_location']], on='ba_brewery_name', how='left')

    # Merging the resulting DataFrame with ratings.csv on 'ba_beer_name' and 'ba_brewery_name'
    merged_df2 = pd.merge(merged_df1, ratings_df_copy_nonan_ba[['ba_beer_name', 'ba_rating', 'ba_overall']], on='ba_beer_name', how='left')

    # Selecting only the desired columns for the final DataFrame and set the scores to numeric type
    final_df_ba = merged_df2[['ba_beer_name', 'ba_brewery_name', 'ba_location', 'ba_rating', 'ba_overall']]
    final_df_ba.columns = ['beer_name', 'brewery_name', 'location', 'ba_rating', 'ba_overall']
    final_df_ba.loc[:, 'ba_rating'] = pd.to_numeric(final_df_ba['ba_rating'], errors='coerce')
    final_df_ba.loc[:, 'ba_overall'] = pd.to_numeric(final_df_ba['ba_overall'], errors='coerce')

    return final_df_ba

##Function to plot the number of beers by rating category and location for rating score for ba website
def plot_rating_and_overall_score_ba(num_countries, final_df_ba, threshold_ba):
    """
    Plots the number of beers by rating and overall score categories for the BA website.

    Parameters:
    ----------
    num_countries (int): Number of top locations to display.
    final_df_ba (pandas.DataFrame): DataFrame containing beer ratings and locations.
    threshold_ba (float): Rating threshold to categorize the beers.
    
    Returns:
    --------
    None
    """
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))  

    ##Rating score
    # Grouping by 'location' and 'rating_category', count for ba and sort by the bigger than threshold category
    location_rating_counts_ba = final_df_ba.groupby(['location', 'rating_category']).size().unstack(fill_value=0).reset_index()
    location_rating_counts_ba = location_rating_counts_ba.sort_values(by=f'bigger than {threshold_ba}', ascending=False)

    # Displaying only the top num_countries
    location_rating_counts_ba = location_rating_counts_ba.head(num_countries)
    
    # Plotting the results for rating score
    x = location_rating_counts_ba['location']
    y1 = location_rating_counts_ba[f'smaller than {threshold_ba}']
    y2 = location_rating_counts_ba[f'bigger than {threshold_ba}']
    axes[0].bar(x, y1, label=f'Smaller than {threshold_ba}', color='skyblue')
    axes[0].bar(x, y2, bottom=y1, label=f'Bigger than {threshold_ba}', color='salmon')
    axes[0].set_xlabel('Location')
    axes[0].set_ylabel('Number of Beers')
    axes[0].set_title(f'Number of Beers by Rating Category and Location (Threshold {threshold_ba})')
    axes[0].legend(title='Rating Score Category')
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha='right')

    ##Overall Score
    # Grouping by 'location' and 'overall_category', count for ba and sort by the bigger than threshold category
    location_overall_counts_ba = final_df_ba.groupby(['location', 'overall_category']).size().unstack(fill_value=0).reset_index()
    location_overall_counts_ba = location_overall_counts_ba.sort_values(by=f'bigger than {threshold_ba}', ascending=False)
    
    #Displaying only the top num_countries
    location_overall_counts_ba = location_overall_counts_ba.head(num_countries)
    
    #Plotting the results for overall score
    y1 = location_overall_counts_ba[f'smaller than {threshold_ba}']
    y2 = location_overall_counts_ba[f'bigger than {threshold_ba}']
    axes[1].bar(x, y1, label=f'Smaller than {threshold_ba}', color='lightgreen')
    axes[1].bar(x, y2, bottom=y1, label=f'Bigger than {threshold_ba}', color='orange')
    axes[1].set_xlabel('Location')
    axes[1].set_ylabel('Number of Beers')
    axes[1].set_title(f'Number of Beers by Overall Category and Location (Threshold {threshold_ba})')
    axes[1].legend(title='Overall Score Category')
    plt.setp(axes[1].get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()  
    plt.show()

def preprocess_final_rb(beers_df_copy, breweries_df_copy, ratings_df_copy_nonan_rb):
    """
    Preprocesses the final DataFrame for RB website data by merging information from beers, breweries, and ratings datasets.

    This function merges beer ratings with brewery locations and final scores to create a clean dataset for RB website.

    Parameters:
    ----------
    beers_df_copy (pandas.DataFrame): DataFrame containing beer details.
    breweries_df_copy (pandas.DataFrame): DataFrame containing brewery details.
    ratings_df_copy_nonan_rb (pandas.DataFrame): DataFrame containing rating details for RB website.

    Returns:
    ---------
    final_df_rb (pandas.DataFrame): Final merged DataFrame with beer, brewery, and rating information for RB.
    """
    # Merging beers.csv and breweries.csv on 'ba_brewery_name' to add 'ba_location' to beers.csv for RB website 
    df_rb_subset = beers_df_copy[['rb_abv', 'rb_avg',
                                'rb_avg_matched_valid_ratings', 'rb_beer_name', 'rb_brewery_name',
                                'rb_nbr_matched_valid_ratings', 'rb_nbr_ratings', 'rb_overall_score',
                                'rb_style', 'rb_style_score', 'rb_zscore']]
    merged_df3 = pd.merge(df_rb_subset, breweries_df_copy[['rb_brewery_name', 'rb_location']], on='rb_brewery_name', how='left')

    # Merging the resulting DataFrame with ratings.csv on 'ba_beer_name' and 'ba_brewery_name'
    merged_df4 = pd.merge(merged_df3, ratings_df_copy_nonan_rb[['rb_beer_name', 'rb_rating', 'rb_overall']], on='rb_beer_name', how='left')

    # Selecting only the desired columns for the final DataFrame and set the scores to numeric type
    final_df_rb = merged_df4[['rb_beer_name', 'rb_brewery_name', 'rb_location', 'rb_rating', 'rb_overall']]
    final_df_rb.columns = ['beer_name', 'brewery_name', 'location', 'rb_rating', 'rb_overall']

    final_df_rb.loc[:,'rb_rating'] = pd.to_numeric(final_df_rb['rb_rating'], errors='coerce')
    final_df_rb.loc[:,'rb_overall'] = pd.to_numeric(final_df_rb['rb_overall'], errors='coerce')

    return final_df_rb

##Function to plot the number of beers by rating category and location for rating score for rb website
def plot_rating_and_overall_score_rb(num_countries, final_df_rb, threshold_rating_rb, threshold_overall_rb):
    """
    Plots the number of beers by rating category and overall score for different locations (countries).


    Parameters:
    ----------
    num_countries : int
        The number of top countries (locations) to display in the plots.
        
    final_df_rb : pd.DataFrame
        The dataframe containing the beer data. 
        
    threshold_rating_rb : float
        The threshold value used to classify beers into "smaller than" or "bigger than" the rating score threshold.
        
    threshold_overall_rb : float
        The threshold value used to classify beers into "smaller than" or "bigger than" the overall score threshold.

    Returns:
    -------
    None
        This function does not return any value. It generates and displays two bar plots.

    """
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))  

    ##Rating score
    # Grouping by 'location' and 'rating_category', count for rb and sort by the bigger than threshold category
    location_rating_counts_rb = final_df_rb.groupby(['location', 'rating_category']).size().unstack(fill_value=0).reset_index()
    location_rating_counts_rb = location_rating_counts_rb.sort_values(by=f'bigger than {threshold_rating_rb}', ascending=False)

    # Displaying only the top num_countries
    location_rating_counts_rb= location_rating_counts_rb.head(num_countries)
    
    # Plotting the results for rating score
    x = location_rating_counts_rb['location']
    y1 = location_rating_counts_rb[f'smaller than {threshold_rating_rb}']
    y2 = location_rating_counts_rb[f'bigger than {threshold_rating_rb}']
    axes[0].bar(x, y1, label=f'Smaller than {threshold_rating_rb}', color='skyblue')
    axes[0].bar(x, y2, bottom=y1, label=f'Bigger than {threshold_rating_rb}', color='salmon')
    axes[0].set_xlabel('Location')
    axes[0].set_ylabel('Number of Beers')
    axes[0].set_title(f'Number of Beers by Rating Category and Location (Threshold {threshold_rating_rb})')
    axes[0].legend(title='Rating Score Category')
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha='right')

    ##Overall Score
    # Grouping by 'location' and 'rating_category', count for rb and sort by the bigger than threshold category
    location_overall_counts_rb = final_df_rb.groupby(['location', 'overall_category']).size().unstack(fill_value=0).reset_index()
    location_overall_counts_rb = location_overall_counts_rb.sort_values(by=f'bigger than {threshold_overall_rb}', ascending=False)

    # Displaying only the top num_countries
    location_overall_counts_rb= location_overall_counts_rb.head(num_countries)

    # Plotting the results for overall score
    y1 = location_overall_counts_rb[f'smaller than {threshold_overall_rb}']
    y2 = location_overall_counts_rb[f'bigger than {threshold_overall_rb}']
    axes[1].bar(x, y1, label=f'Smaller than {threshold_overall_rb}', color='lightgreen')
    axes[1].bar(x, y2, bottom=y1, label=f'Bigger than {threshold_overall_rb}', color='orange')
    axes[1].set_xlabel('Location')
    axes[1].set_ylabel('Number of Beers')
    axes[1].set_title(f'Number of Beers by Overall Category and Location (Threshold {threshold_overall_rb})')
    axes[1].legend(title='Overall Score Category')
    plt.setp(axes[1].get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()  
    plt.show()
