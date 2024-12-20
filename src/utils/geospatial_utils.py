import numpy as np
import pandas as pd
import os
import torch
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Geospatial analyses
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from collections import Counter

# Visualization libraries
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.io as pio

def load_geotiff(file_name):
    ''' Load .tiff files containing climatic data
    
    Input:
        file_name: str
            Path to .tiff file

    Output:
        data: np.array
            2d downscaled array containing climatic values in each pixel
    
    '''
    
    _ = np.newaxis
    # downsampling_layer = torch.nn.MaxPool2d(kernel_size=10, stride=10)
    downsampling_layer = torch.nn.AvgPool2d(kernel_size=10, stride=10)
    # downsampling_layer = torch.nn.Conv2d(1, 1, kernel_size=10, stride=10)

    with rasterio.open(file_name) as src:
        array = src.read(1, out_dtype=np.float32)
        data = downsampling_layer(torch.tensor(array[_,_,:,:], dtype=torch.float32)).detach().numpy()

    return data[0,0]


def animation_belgium(world, clim_data, variable):
    ''' Create an animation of yearly climatic variable in Belgium
    
    Input:
        world: gpd.GeoDataFrame
            Geometries of all countries, previously downloaded from naturalearth dataset

        clim_data: np.array of size (12, 2088, 4320)
            Climatic variable data for 12 months acrosse the world
        
        variable: str
            Specifies the unit of the axis

    Output:
        anim: .gif
            animation in saved as a .gif format

    '''

    belgium = world[world["ADMIN"] == "Belgium"]

    pixel_size = 360 / clim_data[0].shape[1]
    transform = from_origin(-180, 90, pixel_size, pixel_size)

    mask = geometry_mask(
            geometries=belgium["geometry"].values,
            out_shape=clim_data[0].shape,
            transform=transform,
            invert=True  # True where the geometry is located
        )
    
    # Generate animation

    if (variable == "tmean") or(variable == "tmin") or (variable == "tmax"):
        label = "Temperature [°C]"
    elif variable == "prec":
        label = "Precipitation [mm]"
    else:
        label = ""

    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = 'seismic'

    vmin = 0
    vmax = 30
    norm = Normalize(vmin=vmin, vmax=vmax)

    # add legend
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label(f"{label}")  # Label the color bar with the variable name
    

    def update(frame):
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
        ax.clear()  # Clear previous plot

        masked_data = np.where(mask, clim_data[frame], np.nan)

        ax.imshow(masked_data, cmap=cmap, vmin=vmin , vmax=vmax)  # Initialize with the first frame
        ax.set_title(f"{months[frame]}")
        ax.set_axis_off()
        ax.set_xlim(2180,2240)
        ax.set_ylim(450,500)

    # Create the animation
    anim = FuncAnimation(fig, update, frames=range(12), repeat=True)

    # Save the animation as a GIF file
    #anim.save(f"output/animations/belgium_{variable}.gif", writer="pillow", fps=3)


def interpolate_temp(data, map_gdf):
    """
    Interpolate the average temperature per country.

    Input:
        data: np.array of shape (2088, 4320)
            Climatic data
        map_gdf: gpd.GeoDataFrame
            Contains geometries of regions or countries

    Output:
        mean_values: list
            interpolated mean climatic value per region of map_gdf
    """
    # Define pixel size and transformation for WGS84
    pixel_size = 360 / data.shape[1]  # Calculate pixel size dynamically based on array dimensions
    transform = from_origin(-180, 90, pixel_size, pixel_size)

    mean_values = []

    # Loop through each country and compute the mean temperature
    for _, country in map_gdf.iterrows():
        # Convert country geometry to GeoJSON format
        geom = [country['geometry'].__geo_interface__]

        # Create a mask for the current country geometry
        mask = geometry_mask(
            geometries=geom,
            out_shape=data.shape,
            transform=transform,
            invert=True  # True where the geometry is located
        )

        # Apply mask to the temperature data
        masked_data = np.where(mask, data, np.nan)

        # Calculate the mean temperature for the country, ignoring NaNs
        mean = np.nanmean(masked_data)
        mean_values.append(mean)

    return mean_values

def generate_usgdfs(us, tmean_data, prec_data):
    ''' 
    Interpolates climatic data for USA states, for each month of the year and store monthly gdf in a list
    
    Input:
        us: gpd.GeoDataFrame
            Geometries of USA states, previously downloaded from naturalearth dataset

        tmean_data: np.array of size (12, 2088, 4320)
            Temperature data for 12 months acrosse the world

        prec_data: np.array of size (12, 2088, 4320)
            Precipitation data for 12 months acrosse the world
    
    '''

    t_stats = np.zeros((12, 49))
    p_stats = np.zeros((12, 49))

    # Append a gdf per month in the list us_gdfs
    # Standardize the temperature and precipitation data
    for i in range(12):
        t_stat = interpolate_temp(tmean_data[i,:,:], us)
        p_stat = interpolate_temp(prec_data[i,:,:], us)
        t_stats[i] = t_stat #(t_stat - us_mean_temp) / us_std_temp
        p_stats[i] = p_stat #(p_stat - us_mean_prec) / us_std_prec

    # Normalize temperature and precipitation data
    av_tmean_states = np.mean(t_stats)
    std_tmean_states = np.std(t_stats)
    av_prec_states = np.mean(p_stats)
    std_prec_states = np.std(p_stats)

    # create list of geodataframe with interpolated climatic data (one per month)
    us_gdfs = []

    for j in range(12):
        gdf = us.copy()
        gdf['tmean'] = (t_stats[j] - av_tmean_states) / std_tmean_states
        gdf['prec'] = (p_stats[j] - av_prec_states) / std_prec_states
        us_gdfs.append(gdf)

    return us_gdfs, t_stats, p_stats


def plot_usa(us_gdfs, variable):
    ''' Plots a map of a given climatic variable in the USA.
    
    Input: 
        us_gdfs: list of gpd.GeoDataFrame
            Contains monthly climatic data and geometries of USA states
        
        variable: str
            Specifies the unit of the axis
            
    '''
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
    
    if variable == 'tmean':
        name = 'mean temperature'
    elif variable == 'prec':
        name = 'precipitation'
    else:
        print("Please enter valid 'variable' name")
    
    fig, axs = plt.subplots(3, 4, figsize=(20, 15))
    axs = axs.ravel()

    all = [gdf[variable].values for gdf in us_gdfs]
    vmin = min([value.min() for value in all])
    vmax = max([value.max() for value in all])

    # normalize all data!!
    for i, ax in enumerate(axs):
        # im = axs[i].imshow(temp_data[i], cmap='hot')  # Initialize with the first frame
        # cbar = plt.colorbar(im, ax=axs[i])
        # cbar.set_label('Color Intensity')  # Optionally, add a label to the colorbar


        us_gdfs[i].plot(column=variable, ax=ax, legend=True, cmap='seismic', vmin=vmin, vmax=vmax,
                        legend_kwds={'label': f"Average {name}",
                                    'orientation': 'horizontal'},
                        missing_kwds={'color': 'lightgrey'})
        ax.set_title(f'{months[i]}')
        ax.axis('off')  # Turn off the axis 

    fig.suptitle(f"Monthly {name} in the United States")
    plt.tight_layout()
    plt.show()


def generate_geodf(df, world):
    ''' Generate a GeoDataFrame with national information on beer preferences (average ratings, ...)
    and geometry information about the country, as to be able to generate world map of different beer-related
    variables.
    
    Input: 
        df: pd.DataFrame
            Cleaned dataset, including user_country
        world: gpd.GeoDataFrame
            Geometries of all countries, previously downloaded from naturalearth dataset
    
    Output:
        geo_df: gpd.GeoDataFrame
            National statistics on beer preferences and geometries of every country
        
    '''
    # Group by user_country and compute national statistics
    grouped_df = df.groupby(by="country_user").aggregate({'rating': 'mean', 'appearance': 'mean', 'aroma': 'mean', 
                                                      'palate': 'mean', 'taste': 'mean', 'overall': 'mean', 
                                                      'style': list, 'abv': 'count'})
    
    # Map differences in country names formatting to allow merging
    map = {
    'United States': 'United States of America',
    'Ivory Coast': 'United Republic of Tanzania',
    'Russia': 'Russian Federation',
    'United Kingdom': 'England',
    'Czech Republic': 'Czechia',
    'South Korea': 'Republic of Korea',
    'North Korea': 'Democratic People\'s Republic of Korea',
    'Syria': 'Syrian Arab Republic',
    'Laos': 'Lao People\'s Democratic Republic',
    'Palestine': 'State of Palestine',
    'Cape Verde': 'Cabo Verde',
    'Swaziland': 'Eswatini',
    'Micronesia': 'Federated States of Micronesia',
    'Vatican City': 'Holy See',
    'Macedonia': 'North Macedonia',
    'East Timor': 'Timor-Leste',
    'Moldova': 'Republic of Moldova',
    'Iran': 'Islamic Republic of Iran',
    'Tanzania': 'United Republic of Tanzania',
    'Bolivia': 'Bolivia (Plurinational State of)',
    'Venezuela': 'Venezuela (Bolivarian Republic of)',
    'Brunei': 'Brunei Darussalam',
    'South Sudan': 'Republic of South Sudan',
    'Myanmar': 'Myanmar (Burma)',
    'Gambia': 'The Gambia',
    'Bahamas': 'The Bahamas',
    'Congo': 'Democratic Republic of the Congo',
    'Republic of the Congo': 'Congo',
    'Vietnam': 'Viet Nam',
    'Antigua': 'Antigua and Barbuda',
    'Trinidad': 'Trinidad and Tobago',
    'Saint Kitts': 'Saint Kitts and Nevis',
    'Saint Vincent': 'Saint Vincent and the Grenadines',
    'Saint Lucia': 'Saint Lucia',
    'Western Sahara': 'Sahrawi Arab Democratic Republic'
    }

    grouped_df = grouped_df.rename(index=map)

    # Left merge on world["ADMIN"] (country name)
    geo_df = world.merge(grouped_df, left_on="ADMIN", right_index=True, how="left")

    # computation of log(count) and replacing NAN values for visualization purposes
    geo_df['log_count'] = np.log(geo_df["abv"])
    geo_df.drop(columns="abv")
    geo_df.fillna(0, inplace=True)

    return geo_df

def plot_geodf(geo_df):
    ''' Plot national beer preferences statistics on a world map
    
    Input:
        geo_df: gpd.GeoDataFrame
            Contains geometries of all countries and data about national beer preferences
            
    '''

    fig, ax = plt.subplots(1, 2, figsize=(20, 6))

    geo_df.plot(column="log_count", ax=ax[0], legend=True, legend_kwds={'label': "Logarithmic count of reviews per country",
                            'location': 'bottom'})
    ax[0].set_title('Number of ratings per country')
    ax[0].axis('off')

    geo_df.plot(column="rating", ax=ax[1], legend=True, vmin=0.1, vmax=5, legend_kwds={'label': "Average rating per country",
                            'location': 'bottom'})
    ax[1].set_title('Average rating per country')
    ax[1].axis('off')

    plt.tight_layout()
    plt.show()

def get_season(date):
    ''' Map pd.datetime month to a season label
    
    Input:
        date: pd.datetime object

    Output:
        label: int

    '''
    if date.month in [12, 1, 2]:
        return 1
    elif date.month in [3, 4, 5]:
        return 2
    elif date.month in [6, 7, 8]:
        return 3
    else:
        return 4

def get_top_styles_per_season(df):
    return df.groupby('season_num').apply(lambda x: x.nlargest(5, 'rating').sort_values(by='season_num', ascending=True)).reset_index(drop=True)
    
def get_season_name(season_num):
    if season_num == 1:
        return "Winter"
    elif season_num == 2:
        return "Spring"
    elif season_num == 3:
        return "Summer"
    else:
        return "Fall"



def plot_seasonal_preferences(top_styles_per_season):
    # Adding unique colors for each beer style
    color_mapping = {
        "American Amber / Red Ale": "peru",
        "American Black Ale": "maroon",
        "American Double / Imperial Stout": "brown",
        "Quadrupel (Quad)": "olive",
        "Gueuze": "cornflowerblue",
        "Lambic - Unblended": "#bafa37",
        "Faro": "pink",
        "Lambic - Fruit": "yellowgreen",
        "Maibock / Helles Bock": "lightblue",
        "Russian Imperial Stout": "cadetblue",
        "Eisbock": "midnightblue",
        "American Brown Ale": "darkred"
    }

    # Map styles to colors
    bar_colors = [color_mapping[style] for style in top_styles_per_season["style"]]

    fig = go.Figure()
    fig.add_bar(
        x=[top_styles_per_season["season"], top_styles_per_season["style"]],
        y=top_styles_per_season["rating"],
        marker=dict(color=bar_colors),
        width=0.8  # Increase the bar width
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Top Beer Styles by Season in Belgium",
            x=0.5,  # Center the title
            xanchor='center'
        ),
        xaxis=dict(
            title='',
            tickangle=-72,
            title_font_size=2,
            categoryorder='array',
            categoryarray=['Winter', 'Spring', 'Summer', 'Fall'],
            showgrid=False,
        ),
        yaxis=dict(title='Rating', range=[3, 5]),  # Set y-axis range
        legend_title="Beer Style",
        height=600,  # Increase plot height for better visualization
    )

    # fig.write_image("website/assets/figures/analysis2_plot.svg")
    #pio.write_html(fig, file="analysis2_plot.html", full_html=True)
    #plt.savefig('analysis2_plot.png', bbox_inches='tight')
    fig.show()

def find_coordinates(data, us):

    # Define pixel size and transformation for WGS84
    pixel_size = 360 / data.shape[1]  # Calculate pixel size dynamically based on array dimensions
    transform = from_origin(-180, 90, pixel_size, pixel_size)
    inverse_transform = ~transform

    # Compute the union of all US states geometries
    us_geometries = [shape(geom.__geo_interface__) for geom in us["geometry"].values]
    us_union_geometry = unary_union(us_geometries)

    us_mask = geometry_mask(
        geometries=[us_union_geometry],
        out_shape=data.shape,
        transform=transform,
        invert=True  # True where the geometry is located
    )

    # Find indices of pixels where the `us_mask` is True
    us_pixel_indices = np.argwhere(us_mask)

    # Convert indices to geographic coordinates
    us_pixel_coords = [(transform * (col, row)) for row, col in us_pixel_indices]

    return us_pixel_indices, us_pixel_coords, inverse_transform


def data_preparation(tmean_data, prec_data, us):

    us_pixel_indices, us_pixel_coords, inverse_transform = find_coordinates(tmean_data[0], us)
    
    lon = [x[0] for x in us_pixel_coords]
    lat = [x[1] for x in us_pixel_coords]
    us_df = pd.DataFrame({"lat": lat, "lon": lon})

    lon_idx = [x[0] for x in us_pixel_indices]
    lat_idx = [x[1] for x in us_pixel_indices]

    # standardize data
    tmean_us = np.zeros((len(lat), 12)) 
    prec_us = np.zeros((len(lat), 12))

    for i in range(12):
        tmean_us[:,i] = tmean_data[i][lon_idx, lat_idx]
        prec_us[:,i] = prec_data[i][lon_idx, lat_idx]

    tmean_scaler = StandardScaler().fit(tmean_us)
    prec_scaler = StandardScaler().fit(prec_us)

    tmean_us = tmean_scaler.transform(tmean_us)
    prec_us = prec_scaler.transform(prec_us)

    for j in range(12):
        new_tmean_col = "tmean_" + str(j+1)
        new_prec_col = "prec_" + str(j+1)

        us_df[new_tmean_col] = tmean_us[:,j]
        us_df[new_prec_col] = prec_us[:,j]

    return us_df, tmean_scaler, prec_scaler

def swiss_data_preparation(tmean_data, prec_data, switzerland, tmean_scaler, prec_scaler):

    ch_pixel_indices, ch_pixel_coords, _ = find_coordinates(tmean_data[0], switzerland)

    lon = [x[0] for x in ch_pixel_coords]
    lat = [x[1] for x in ch_pixel_coords]
    ch_df = pd.DataFrame({"lat": lat, "lon": lon})

    lon_idx = [x[0] for x in ch_pixel_indices]
    lat_idx = [x[1] for x in ch_pixel_indices]

    # standardize daza
    tmean_ch = np.zeros((len(lat), 12)) 
    prec_ch = np.zeros((len(lat), 12))

    for i in range(12):
        tmean_ch[:,i] = tmean_data[i][lon_idx, lat_idx]
        prec_ch[:,i] = prec_data[i][lon_idx, lat_idx]

    tmean_ch = tmean_scaler.transform(tmean_ch)
    prec_ch = prec_scaler.transform(prec_ch)

    for j in range(12):
        new_tmean_col = "tmean_" + str(j+1)
        new_prec_col = "prec_" + str(j+1)

        ch_df[new_tmean_col] = tmean_ch[:,j]
        ch_df[new_prec_col] = prec_ch[:,j]
    
    return ch_df

def get_kmean_score(n, us_df):

    clustering_cols = ['tmean_1', 'prec_1', 'tmean_2', 'prec_2', 'tmean_3',
       'prec_3', 'tmean_4', 'prec_4', 'tmean_5', 'prec_5', 'tmean_6', 'prec_6',
       'tmean_7', 'prec_7', 'tmean_8', 'prec_8', 'tmean_9', 'prec_9',
       'tmean_10', 'prec_10', 'tmean_11', 'prec_11', 'tmean_12', 'prec_12']
    
    kmeans = KMeans(n_clusters=n, random_state=0, n_init="auto").fit(X=us_df[clustering_cols])
    score = kmeans.score(X=us_df[clustering_cols])
    return score


def weather_clustering(us_df, ch_df):

    clustering_cols = ['tmean_1', 'prec_1', 'tmean_2', 'prec_2', 'tmean_3',
       'prec_3', 'tmean_4', 'prec_4', 'tmean_5', 'prec_5', 'tmean_6', 'prec_6',
       'tmean_7', 'prec_7', 'tmean_8', 'prec_8', 'tmean_9', 'prec_9',
       'tmean_10', 'prec_10', 'tmean_11', 'prec_11', 'tmean_12', 'prec_12']
    
    scores = np.zeros(len(range(2,9)))
    n_clusters = np.arange(2, 9)

    for n in n_clusters:
        scores[n-2] = get_kmean_score(n, us_df)

    # choose n_cluster = 5 for next analysis

    kmeans_5 = KMeans(n_clusters=5, random_state=0, n_init="auto").fit(X=us_df[clustering_cols])
    labels = kmeans_5.labels_
    ch_labels = kmeans_5.predict(X=ch_df[clustering_cols])

    clustered_df = pd.DataFrame({"lat": us_df['lat'], "lon": us_df['lon'], "labels": labels})

    return clustered_df, n_clusters, scores, ch_labels

def interpolate_labels(clustered_df, us_df):
    """
    Interpolates the labels for each state based on majority voting of points in clustered_df.

    Parameters:
        clustered_df (pd.DataFrame): DataFrame containing longitude ('lon'), latitude ('lat'), and labels ('labels').
        us_gdf (gpd.GeoDataFrame): GeoDataFrame containing state geometries.

    Returns:
        list: List of labels (int) assigned to each state based on majority voting.
    """
    # Convert clustered_df to a GeoDataFrame
    clustered_gdf = gpd.GeoDataFrame(
        clustered_df,
        geometry=gpd.points_from_xy(clustered_df['lon'], clustered_df['lat']),
        crs=us_df.crs
    )

    clustered_gdf = clustered_gdf.to_crs(us_df.crs)
    joined_gdf = gpd.sjoin(clustered_gdf, us_df, how="inner", predicate="intersects")

    majority_labels = []

    # Iterate over each state in us_gdf
    for state_index, state_row in us_df.iterrows():
        points_in_state = joined_gdf[joined_gdf.index_right == state_index]

        if not points_in_state.empty:
            label_counts = Counter(points_in_state['labels'])
            majority_label = label_counts.most_common(1)[0][0]
        else:
            # Handle cases with no points in a state (e.g., assign -1 as no label)
            majority_label = -1

        majority_labels.append(majority_label)

    return majority_labels

def get_best_rated(data_usa):

    usa_grouped = (
    data_usa.groupby(by=["location_user", "style"])[["overall"]]
    .agg(overall=('overall', 'mean'), review_count=('overall', 'size'))
    .reset_index()
    )

    usa_grouped['location_user'] = usa_grouped['location_user'].str.replace('United States, ', '', regex=False)
    usa_grouped = usa_grouped[usa_grouped["review_count"] >= 40]

    best_rated_per_state = usa_grouped.loc[usa_grouped.groupby('location_user')['overall'].idxmax()]

    best_rated_per_state = best_rated_per_state.reset_index(drop=True)

    best_rated_per_state = best_rated_per_state[
        ~best_rated_per_state['location_user'].isin(['Hawaii', 'Alaska'])
    ]

    return best_rated_per_state

def get_favbeer_map(merged_gdf):

    label_4_group = merged_gdf[merged_gdf["labels"] == 4]

    # Step 2: Count the occurrences of each beer style
    top_beer_styles = label_4_group["style"].value_counts()

    # Step 3: Get the top 3 beer styles
    top_3_beer_styles = top_beer_styles.head(3)

    print("Top 3 beer style in cluster 2 (same cluster as Lausanne): ")
    for i, beer in enumerate(top_3_beer_styles.index):
        print(f" {i+1}. {beer}")


    clustered_df = (
        merged_gdf.groupby('labels').agg({
            'geometry': lambda x: unary_union(x),  # Perform union operation on geometry
            'style': lambda x: x.mode()[0]  # Majority voting for the most common style
        }).reset_index()
    )

    favbeer_map = {}

    for _, row in clustered_df.iterrows():
        favbeer_map[row['labels']] = row['style']

    return favbeer_map

def generate_analysis4_plot(us, n_clusters, kmeans_score, clustered_df, favbeer_map):

    fig, ax = plt.subplots(2, 2, figsize=(20,11))
    ax = ax.ravel()

    # 1st plot - Weather data clustering
    us.plot(ax=ax[0], color='lightgray')
    markersize = 0.005

    label_colors = {
        0: 'mistyrose',
        1: 'indianred',
        2: 'powderblue',
        3: 'cadetblue',
        4: 'lightcoral',
    }

    clustered_df['color'] = clustered_df['labels'].map(label_colors)

    ax[0].scatter(
        clustered_df['lon'], 
        clustered_df['lat'], 
        c=clustered_df['color'],  
        s=10,  
        alpha=0.7  
    )

    for label, color in label_colors.items():
        ax[0].scatter([], [], color=color, label=f'{label+1}')

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=f'Label {label+1}') for label, color in label_colors.items()]
    ax[0].legend(handles=handles, title="Labels", loc='lower right', fontsize='small')

    ax[0].set_title('Clustering on monthly mean temperature and precipitation in the USA')
    ax[0].set_xlabel('Longitude')
    ax[0].set_ylabel('Latitude')
    ax[0].axis('off')

    # 2nd plot - Clustering metric

    ax[1].plot(n_clusters, -kmeans_score, color="indianred")
    ax[1].set_xlabel("number of cluster")
    ax[1].set_ylabel("MSE Score")
    ax[1].set_title("MSE Score vs number of clusters")

    # 3rd plot - Weather interpolation per state

    us.plot(ax=ax[2], color='lightgray')

    us['color'] = us['labels'].map(label_colors)
    us.plot(ax=ax[2], color=us['color'], edgecolor='black', linewidth=0.05)


    handles = [ plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=f'Label {label+1}') for label, color in label_colors.items()]
    ax[2].legend(handles=handles, title="Labels", loc='lower right', fontsize='small')

    ax[2].set_title('Interpolation of the climatic clusters per state')
    ax[2].set_xlabel('Longitude')
    ax[2].set_ylabel('Latitude')
    ax[2].axis('off')

    # 4th plot - beer preferences per clustered states
    us.plot(ax=ax[3], color='lightgray')

    favbeer_color = {
        'American Double / Imperial IPA': 'darkgoldenrod', #'American Double / Imperial IPA',
        'Quadrupel (Quad)': 'tan', #'Quadrupel (Quad)',
        'India Pale Ale (IPA)': 'lemonchiffon'
    }

    us['favbeer'] = us['labels'].map(favbeer_map)
    us['favbeer_color'] = us['favbeer'].map(favbeer_color)

    us.plot(ax=ax[3], color=us['favbeer_color'], edgecolor='black', linewidth=0.05)

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=f'{label}') for label, color in favbeer_color.items()]
    ax[3].legend(handles=handles, title="Favorite beer style", loc='lower right', fontsize='small')

    ax[3].set_title('Best-rated beer style per clustered region')
    ax[3].axis('off')  

    #plt.savefig('analysis4_plot.svg', format='svg', bbox_inches='tight')
    #plt.savefig('analysis4_plot.png', format='png', bbox_inches='tight')
    plt.show()

def plot_switzerland(switzerland, ch_df, ch_labels):

       ch_df['labels'] = ch_labels

       # plot clustering on a map
       fig, ax = plt.subplots()

       # 1st plot - Weather data clustering
       switzerland.plot(ax=ax, color='lightgray')

       label_colors = {
              0: 'mistyrose',
              1: 'indianred',
              2: 'powderblue',
              3: 'cadetblue',
              4: 'lightcoral',
       }

       label_colors_min = {
              0: 'mistyrose',
              3: 'cadetblue',
              4: 'lightcoral',
       }

       ch_df['color'] = ch_df['labels'].map(label_colors)

       ax.scatter(
              ch_df['lon'], 
              ch_df['lat'], 
              c=ch_df['color'],  
              s=30,  
              alpha=0.7  
       )

       ax.plot(6.63282, 46.516, marker='*', color='black', markersize=10, label='Lausanne')

       for label, color in label_colors.items():
              ax.scatter([], [], color=color, label=f'{label+1}')

       handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=f'Label {label+1}') for label, color in label_colors_min.items()]
       handles.append(plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='black', markersize=15, label='Lausanne'))
       ax.legend(handles=handles, title="Labels", loc='lower right', fontsize='small')

       ax.set_title("Weather clustering on Switzerland's map")
       ax.set_xlabel('Longitude')
       ax.set_ylabel('Latitude')
       ax.axis('off')

       plt.savefig('switzerland_plot.svg', format='svg', bbox_inches='tight')
       plt.savefig('switzerland_plot.png', format='png', bbox_inches='tight')

       plt.show()
