import pandas as pd
import numpy as np
import time
import sqlite3

def dump_text_file_to_sqlite(file_path: str, table_name:str, BLK_SIZE:int=100_000, DB_RELATIVE_PATH:str='../local_data/'):
    """ Load big text file to an SQLite DB (for processing data)
    (Inspired from chatGPT code proposition)
    Args:
        file_path (str): Path of the text file to read (.txt)
        BLK_SIZE (int, optional): Block size for memory efficiency. Defaults to 100_000.
    """
    # Step 1: Connect to SQLite database (or create it)
    conn = sqlite3.connect(DB_RELATIVE_PATH + "all_reviews.db")
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone() is not None

    #  Drop the table if it exists
    if table_exists:
        print(f"DROPPING TABLE {table_name} because already existing in DB!")
        cursor.execute(f"DROP TABLE {table_name}")


    t_last = 0
    DISPLAY_DELAY = 0.3
    anim_index = 0
    c = ['|', '/', '-', '\\']
    filename = file_path.split('/')[-1]
    cols = dict()
    with open(file_path, "r") as f:
        rows = []
        r = [0]
        # Extract columns (key1: val1) until \n
        # Load first data chunk to extract table structure (columns) and data types
        line = f.readline()
        while line != '\n':
            values = line.strip().split(':')
            # Try to sort for primitive datatypes
            v = ''.join(values[1:]).strip()
            try:
                int(v)
                t='INTEGER'
            except ValueError:
                try:
                    float(v)
                    t='REAL'
                except ValueError:
                    t='TEXT'
            cols[values[0]] = t
            r.append(v)
            line = f.readline()
        # Create table in database
        querry = 'id INTEGER PRIMARY KEY, ' + ', '.join([f"{c} {t}" for c,t in cols.items()])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({querry})")
        count = 1
        rows.append(r)

        r = [count]
        line = f.readline()
        while line != '':
            if line == '\n':
                rows.append(tuple(r))
                count += 1
                r = [count]
            else:
                values = line.strip().split(':')
                r.append(''.join(values[1:]).strip())

            if count % BLK_SIZE == 0:
                print(" "*100, end='\r')
                print("***WRITING DATA BLK TO DB*** ", end='\r', flush=True)
                querry = 'id, ' + ', '.join(cols.keys())
                querry2 = ', '.join(['?']*(len(cols.keys())+1))
                cursor.executemany(f"INSERT INTO {table_name} ({querry}) VALUES ({querry2})", rows)
                conn.commit()
                rows.clear()
            line = f.readline()

            if time.time() - t_last > DISPLAY_DELAY:
                t_last = time.time()
                print('LOADING "{0}" {1}  --> {2} rows created!'.format(filename, c[anim_index % len(c)], count), end='\r', flush=True)
                anim_index += 1                

        # Insert any remaining rows
        if rows:
            querry = 'id, ' + ', '.join(cols.keys())
            querry2 = ', '.join(['?']*(len(cols.keys())+1))
            cursor.executemany(f"INSERT INTO {table_name} ({querry}) VALUES ({querry2})", rows)
            conn.commit()
        print(" "*100, end='\r')
        print("DONE! Created {0} rows".format(count))

    conn.close()

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
