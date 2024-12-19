import pandas as pd
import numpy as np
import time

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

def load_dict_like_text_file(file_path, encoding='utf-8', BLK_SIZE=100, MAX_BLK=10000) -> pd.DataFrame:
    """
    Load a text file with key-value pairs into a dictionary.
    
    Format:

    key1: value1 \n
    key2: value2 \n
    \\n \n
    key1: value1 \n
    key2: value2 \n
    ...

    Parameters
    ----------
    file_path : str
        Path to the text file.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns 'key' and 'value'.
    """
    t_last = 0
    count = 0
    DISPLAY_DELAY = 0.3
    anim_index = 0
    c = ['|', '/', '-', '\\']
    filename = file_path.split('/')[-1]
    with open(file_path, 'r', encoding=encoding) as f:
        df = None
        blk_dict = dict()
        blk_list = list()
        line = f.readline()
        while line != '':
            if line == '\n':
                # Create dataframe if first time with a block
                count += 1
                if df is None:
                    df = pd.DataFrame([blk_dict])
                elif len(blk_list) < BLK_SIZE:
                    blk_list.append(blk_dict.copy())
                else:
                    df = pd.concat([df, pd.DataFrame(blk_list)], ignore_index=True)
                    blk_list.clear()
            else:
                values = line.strip().split(':')
                blk_dict[values[0]] = ''.join(values[1:]).strip()
            if MAX_BLK > 0:
                if df is not None and len(df) >= MAX_BLK:
                    break
            line = f.readline()
            if time.time() - t_last > DISPLAY_DELAY:
                t_last = time.time()
                print('LOADING "{0}" {1} --> {2} rows'.format(filename, c[anim_index % len(c)], count), end='\r', flush=True)
                anim_index += 1
        if len(blk_list) > 0:
            df = pd.concat([df, pd.DataFrame(blk_list)], ignore_index=True)
    print("                                                          ", end='\r')
    print("LOADED '{0}'".format(filename))
    return df

def merge_rb_ba_datasets(rb_ratings: pd.DataFrame, rb_users: pd.DataFrame, 
                         ba_ratings: pd.DataFrame, ba_users: pd.DataFrame, 
                         breweries: pd.DataFrame ) -> pd.DataFrame:
    """ Used to create the merged dataframe containing all the important data from
        both websites.

    Args:
        rb_ratings (pd.DataFrame): ratings from RateBeer
        rb_users (pd.DataFrame): users from RateBeer
        ba_ratings (pd.DataFrame): ratings from BeerAdvocate
        ba_users (pd.DataFrame): users from BeerAdvocate
        breweries (pd.DataFrame): breweries from both websites

    Returns:
        pd.DataFrame: merged dataframe
    """
    # combine users and ratings
    print("[INFO] :: Combining users and ratings from both websites...", end='', flush=True)
    rb_ratings.loc[:, 'user_id'] = rb_ratings.loc[:, 'user_id'].astype(int)
    rb_ratings_no_username = rb_ratings.drop(columns=['user_name'])
    ba_ratings.loc[:, 'user_id'] = ba_ratings.loc[:, 'user_id'].astype(str)
    ba_ratings_no_username = ba_ratings.drop(columns=['user_name'])
    ba_users.loc[:, 'user_id'] = ba_users.loc[:, 'user_id'].astype(str)
    rb_user_ratings = rb_ratings_no_username.join(other=rb_users.set_index('user_id'), on='user_id', how='left')
    ba_user_ratings = ba_ratings_no_username.join(other=ba_users.set_index('user_id'), on='user_id', how='left')
    rb_user_ratings.rename(columns={'location': 'location_user'}, inplace=True)
    ba_user_ratings.rename(columns={'location': 'location_user'}, inplace=True)
    print("OK", flush=True)

    # combine breweries and ratings
    print("[INFO] :: Combining breweries and ratings from both websites...", end='', flush=True)
    rb_breweries = breweries['rb']
    rb_breweries.loc[:, 'id'] = rb_breweries.loc[:, 'id'].astype(int)
    rb_user_ratings.loc[:, 'brewery_id'] = rb_user_ratings.loc[:, 'brewery_id'].astype(int)
    ba_breweries = breweries['ba']
    ba_breweries.loc[:,'id'] = ba_breweries.loc[:,'id'].astype(int)
    ba_user_ratings.loc[:,'brewery_id'] = ba_user_ratings.loc[:,'brewery_id'].astype(int)
    rb_combined_ratings = rb_user_ratings.join(other=rb_breweries.set_index('id'), on='brewery_id', how='left')
    ba_combined_ratings = ba_user_ratings.join(other=ba_breweries.set_index('id'), on='brewery_id', how='left')
    rb_combined_ratings.rename(columns={'location': 'location_brewery'}, inplace=True)
    ba_combined_ratings.rename(columns={'location': 'location_brewery'}, inplace=True)
    print("OK", flush=True)

    # Merge rb and ba with text reviews in a single dataframe
    print("[INFO] :: Merging all datasets together...", end='', flush=True)
    rb_combined_ratings['source'] = 'rb'
    ba_combined_ratings['source'] = 'ba'
    print("OK", flush=True)

    return pd.concat([ba_combined_ratings, rb_combined_ratings], axis=0)

def remove_duplicate_reviews(df_ratings: pd.DataFrame, matched_ratings: pd.DataFrame) -> pd.DataFrame:
    """ Remove duplicate reviews of same user on both website (based on matched dataset)

    Args:
        df_ratings (pd.DataFrame): the ratings dataframe containing all ratings from both website
        matched_ratings (pd.DataFrame): matched dataframe containing the matched review from both websites

    Returns:
        pd.DataFrame: filtered dataframe by keeping only relevant reviews
    """
    m_ratings_ba = matched_ratings['ba']
    df_text_ratings_no_duplicates = df_ratings.reset_index()
    # Making sure user_id is of type str
    m_ratings_ba.loc[:,'user_id'] = m_ratings_ba.loc[:,'user_id'].astype("string")
    m_ratings_ba.loc[:,'beer_id'] = m_ratings_ba.loc[:,'beer_id'].astype(int)
    df_text_ratings_no_duplicates.loc[:,'user_id'] = df_text_ratings_no_duplicates.loc[:,'user_id'].astype("string")
    df_text_ratings_no_duplicates.loc[:,'beer_id'] = df_text_ratings_no_duplicates.loc[:,'beer_id'].astype(int)

    count_before = df_text_ratings_no_duplicates.index.size
    print("Total # of combined ratings before filtering: {0}".format(count_before))
    print("Total # of duplicate ratings to remove: {0}".format(m_ratings_ba.index.size))

    print("[INFO] :: Dropping duplicates...", end='', flush=True)
    idx_to_drop = df_text_ratings_no_duplicates.join(m_ratings_ba.set_index(['user_id', 'beer_id']), on=['user_id','beer_id'], lsuffix='_left', how='inner').index
    df_text_ratings_no_duplicates.drop(index=idx_to_drop, inplace=True)
    print("OK", flush=True)

    count_after = df_text_ratings_no_duplicates.index.size
    print("Total # of combined ratings after filtering: {0} --> Difference: {1}".format(count_after, count_before-count_after))
    return df_text_ratings_no_duplicates

def clean_NA_empty_values(df_dirty: pd.DataFrame) -> pd.DataFrame:
    """ Simple clean for NA values for users and empty text reviews

    Args:
        df_dirty (pd.DataFrame): the dataframe to be cleaned

    Returns:
        pd.DataFrame: the cleaned dataframe
    """
    # Delete the only line with empty text
    print("[INFO] :: Cleaning empty text review...", end='', flush=True)
    df_clean = df_dirty.drop(df_dirty[df_dirty.text.apply(lambda x: len(x) < 1)].index)
    print("OK", flush=True)

    # Drop NA

    # Since brewery location is not NA for the NA user, maybe it is a good approximation to use it as the user's location
    print("[INFO] :: Merging NaN users' location with brewery location...",  end='', flush=True)
    usr_loc_na_idx = df_clean.location_user.isna()
    df_clean.loc[usr_loc_na_idx, 'location_user'] = df_clean.loc[usr_loc_na_idx, 'location_brewery'] 
    print("OK", flush=True)

    return df_clean

def cast_columns_to_right_type(df: pd.DataFrame) -> pd.DataFrame:
    """ Ensure the types of the columns for the ratings are the right ones (prevent later issues)

    Args:
        df (pd.DataFrame): dataframe to be casted

    Returns:
        pd.DataFrame: the new dataframe with right types
    """
    df_out = df.copy()
    print("[INFO] :: Casting columns to right datatype...", end='', flush=True)
    # Casting to 'human readable' dates
    df_out['date'] = df['date'].astype(int)
    df_out['date'] = pd.to_datetime(df_out['date'], unit='s')

    # string columns
    cols = ['beer_name', 'brewery_name', 'style', 'user_name', 'location_user', 'location_brewery', 'text', 'source']
    for c in cols:
        df_out[c] = df_out[c].astype(str)
    # float columns
    df_out['abv'] = df_out['abv'].astype(float)
    print("OK", flush=True)
    
    return df_out

def extract_states_from_country(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    print("[INFO] :: Extracting country for users...", end='', flush=True)
    df_out['country_user'] = df_out['location_user'].apply(lambda x: x.split(',')[0] if len(x.split(',')) > 0 else x)
    print("OK\n[INFO] :: Extracting country for brewery locations...", end='', flush=True)
    df_out['country_brewery'] = df_out['location_brewery'].apply(lambda x: x.split(',')[0] if len(x.split(',')) > 0 else x)
    print("OK\n[INFO] :: Extracting states for users...", end='', flush=True)
    df_out['state_user'] = df_out['location_user'].apply(lambda x: ''.join(x.split(',')[1:]) if len(x.split(',')) > 0 else None)
    print("OK\n[INFO] :: Extracting states for brewery locations...", end='', flush=True)
    df_out['state_brewery'] = df_out['location_brewery'].apply(lambda x: ''.join(x.split(',')[1:]) if len(x.split(',')) > 0 else None)
    print("OK", flush=True)

    return df_out


def get_beer_style_mapping() -> map:
    """ Returns a mapping to group beer style in high levels categories
    (The categories where generated by asking chatGPT)

    Returns:
        map: The mapping (beer_style --> categorie)
    """
    style_categories = {
        'Pale Ale': [
            'English Pale Ale', 'American Pale Ale', 'American Pale Ale (APA)', 'Amber Ale', 'American Amber / Red Ale',
            'Golden Ale/Blond Ale', 'Extra Special / Strong Bitter (ESB)', 'English Bitter', 'Premium Bitter/ESB',
            'English Pale Mild Ale', 'California Common', 'California Common / Steam Beer'
        ],
        'India Pale Ale (IPA)': [
            'American IPA', 'English India Pale Ale (IPA)', 'India Pale Ale (IPA)', 'Imperial IPA',
            'Session IPA', 'Black IPA', 'Belgian IPA', 'American Double / Imperial IPA'
        ],
        'Stout': [
            'American Stout', 'English Stout', 'Foreign / Export Stout', 'Irish Dry Stout', 'Milk / Sweet Stout',
            'Oatmeal Stout', 'Russian Imperial Stout', 'Dry Stout', 'Imperial Stout'
        ],
        'Porter': [
            'English Porter', 'Baltic Porter', 'American Porter', 'Imperial Porter'
        ],
        'Wheat Beer': [
            'American Pale Wheat Ale', 'Hefeweizen', 'Kristalweizen', 'Dunkelweizen', 'Berliner Weissbier',
            'Weizenbock', 'Wheatwine', 'German Hefeweizen', 'German Kristallweizen', 'Wheat Ale'
        ],
        'Lager': [
            'German Pilsener', 'Czech Pilsener', 'Czech Pilsner (Světlý)', 'Euro Pale Lager', 'Pale Lager',
            'American Pale Lager', 'Light Lager', 'American Adjunct Lager', 'Premium Lager', 'American Amber / Red Lager',
            'Märzen / Oktoberfest', 'Amber Lager/Vienna', 'Vienna Lager'
        ],
        'Dark Lager': [
            'Dunkel/Tmavý', 'Euro Dark Lager', 'Munich Dunkel Lager', 'Schwarzbier', 'Dunkler Bock'
        ],
        'Strong Lager': [
            'Maibock / Helles Bock', 'Heller Bock', 'Eisbock', 'Doppelbock', 'Bock', 'American Double / Imperial Pilsner',
            'Imperial Pils/Strong Pale Lager', 'Malt Liquor', 'American Malt Liquor'
        ],
        'Belgian Ale': [
            'Belgian Pale Ale', 'Belgian Dark Ale', 'Belgian Strong Pale Ale', 'Belgian Strong Dark Ale',
            'Belgian Strong Ale', 'Belgian IPA', 'Dubbel', 'Tripel', 'Quadrupel (Quad)', 'Abt/Quadrupel',
            'Abbey Dubbel', 'Abbey Tripel'
        ],
        'Saison & Farmhouse': [
            'Saison / Farmhouse Ale', 'Saison', 'Bière de Garde', 'Bière de Champagne / Bière Brut'
        ],
        'Sour Ale': [
            'American Wild Ale', 'Sour/Wild Ale', 'Berliner Weisse', 'Flanders Red Ale', 'Flanders Oud Bruin',
            'Sour Red/Brown', 'Gose', 'Lambic - Fruit', 'Lambic - Unblended', 'Lambic Style - Fruit', 
            'Lambic Style - Gueuze', 'Gueuze', 'Lambic Style - Unblended', 'Faro', 'Lambic Style - Faro'
        ],
        'Specialty & Seasonal': [
            'Pumpkin Ale', 'Winter Warmer', 'Christmas Ale', 'Spice/Herb/Vegetable', 'Herbed / Spiced Beer',
            'Fruit Beer', 'Fruit / Vegetable Beer', 'Chile Beer', 'Radler/Shandy', 'Braggot', 'Kvass',
            'Mead', 'Rye Beer', 'Scottish Gruit / Ancient Herbed Ale', 'Specialty Grain'
        ],
        'Strong Ale': [
            'English Strong Ale', 'English Barleywine', 'American Barleywine', 'Barley Wine', 'Old Ale', 
            'American Strong Ale', 'Scottish Ale', 'Scotch Ale / Wee Heavy', 'Scotch Ale'
        ],
        'Other Ales': [
            'American Brown Ale', 'English Brown Ale', 'Irish Red Ale', 'Irish Ale', 'English Dark Mild Ale',
            'Mild Ale', 'Traditional Ale', 'American Dark Wheat Ale'
        ],
        'Pilsner': [
            'Pilsener', 'German Pilsener', 'Czech Pilsener', 'Czech Pilsner (Světlý)', 'American Double / Imperial Pilsner'
        ],
        'Low Alcohol': [
            'Low Alcohol Beer', 'Happoshu', 'Low Alcohol'
        ],
        'Hybrid Styles': [
            'Smoked Beer', 'Smoked', 'Sahti', 'Sahti/Gotlandsdricke/Koduõlu', 'Rauchbier', 'Grodziskie/Gose/Lichtenhainer',
            'Kellerbier / Zwickelbier', 'Zwickel/Keller/Landbier', 'California Common', 'California Common / Steam Beer'
        ]
    }
    return {style: category for category, styles in style_categories.items() for style in styles}
