import numpy as np
import pandas as pd
import os
import torch

# Geospatial analyses
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.features import geometry_mask

# Visualization libraries
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
import matplotlib.cm as cm

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
    anim.save(f"output/animations/belgium_{variable}.gif", writer="pillow", fps=3)


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