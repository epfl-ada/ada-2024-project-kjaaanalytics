# imports
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


#### Fun fact #1 - Bob travels from Switzerland to UK (using rating score column)

# Defining a function to prepare the dataframe used to plot average rating score vs Beer style (funfact1)
def df_funfact_1(beers_df_copy):
    """
    Analyze beer ratings in Switzerland and England by style category.
    This function processes a DataFrame containing beer data to compare 
    average ratings between Switzerland and England across various style categories. 

    Parameters:
    ----------
    beers_df_copy : pandas.DataFrame
        A DataFrame containing beer data. 

    Returns:
    -------
    tuple : 
        - merged_rating_funfact_1_df (pandas.DataFrame): A merged DataFrame
          containing average ratings for each style category for both countries 
          before pivoting.
        - pivot_rating_sorted_funfact_1_df (pandas.DataFrame): A pivoted DataFrame
          with style categories as rows, Switzerland's and England's average 
          ratings as columns, and additional columns for rating differences and 
          absolute rating differences.

    """
    # Filtering data for Switzerland and England
    switzerland_data = beers_df_copy[beers_df_copy['country_user'] == 'Switzerland']
    england_data = beers_df_copy[beers_df_copy['country_user'] == 'England']

    # Grouping  by 'style' and 'country_brewery' and calculate average ratings
    switzerland_avg_rating = switzerland_data.groupby(['style_category', 'country_user'])['rating'].mean().reset_index()
    switzerland_avg_rating['country_user'] = 'Switzerland'

    england_avg_rating = england_data.groupby(['style_category', 'country_user'])['rating'].mean().reset_index()
    england_avg_rating['country_user'] = 'England'

    # Merging the two DataFrames to get common styles
    merged_rating_funfact_1_df = pd.concat([switzerland_avg_rating, england_avg_rating])

    # Sorting the data by 'rating' in descending order
    merged_rating_funfact_1_df =  merged_rating_funfact_1_df.sort_values(by='rating', ascending=False)

    # Pivoting the DataFrame so that each country has its own column
    pivot_rating_funfact_1_df = merged_rating_funfact_1_df.pivot(index='style_category', columns='country_user', values='rating')
    pivot_rating_funfact_1_df.columns.name = None
    pivot_rating_funfact_1_df = pivot_rating_funfact_1_df.reset_index()

    # Calculating the difference between the ratings for each style
    pivot_rating_funfact_1_df['rating_diff'] = pivot_rating_funfact_1_df['Switzerland'] - pivot_rating_funfact_1_df['England']

    # Sorting by the absolute value of the difference 
    pivot_rating_funfact_1_df['abs_rating_diff'] = pivot_rating_funfact_1_df['rating_diff'].abs()
    pivot_rating_sorted_funfact_1_df = pivot_rating_funfact_1_df.sort_values(by='abs_rating_diff', ascending=False)

    return merged_rating_funfact_1_df, pivot_rating_sorted_funfact_1_df


# Defining a function to create the plot for funfact_1
def plot_funfact_1(num_styles, pivot_rating_sorted_funfact_1_df, merged_rating_funfact_1_df):
    """
    Plot the top N beer styles by average rating for Switzerland and England.
    This function generates a bar chart using Plotly to compare the average 
    rating scores of the top N beer styles for Switzerland and England.

    Parameters:
    ----------
    num_styles : int
        The number of beer styles to include in the plot, based on 
        average rating differences.
    pivot_rating_sorted_funfact_1_df : pandas.DataFrame
        A pivoted DataFrame containing style categories, Switzerland's and 
        England's average ratings, rating differences, and absolute rating 
        differences.
    merged_rating_funfact_1_df : pandas.DataFrame
        A merged DataFrame with average ratings for each style category for 
        both Switzerland and England before pivoting.

    Returns:
    -------
    None
        The function displays the Plotly bar chart but does not return any 
        value.
    """
    # Filtering the data for the top N styles by average rating
    top_styles_rating_df = pivot_rating_sorted_funfact_1_df.head(num_styles)

    # Ensuring the order of styles matches the descending order in top_styles_df
    style_order_rating = top_styles_rating_df['style_category'].tolist()

    # Merging back to include country data
    filtered_rating_df = merged_rating_funfact_1_df[merged_rating_funfact_1_df['style_category'].isin(top_styles_rating_df['style_category'])]

    # Plotting bar chart using Plotly
    fig = px.bar(
        filtered_rating_df,
        x='style_category',
        y='rating',
        color='country_user',
        category_orders={'style_category': style_order_rating},  
        title=f'Comparison of the {num_styles} Beer Styles by Average Rating Score in Switzerland vs England',
        labels={'style_category': 'Beer Style', 'rating': 'Average Rating Score'},
        barmode='group', 
        color_discrete_sequence=px.colors.qualitative.Pastel  
    )

    # Enhancing chart appearance
    fig.update_layout(
        title={
            'text': f'Comparison of the {num_styles} Beer Styles by Average Rating Score in Switzerland vs England',
            'x': 0.5,  
            'xanchor': 'center', 
            'yanchor': 'top',
            'font': {'size': 20}  
        },
        xaxis_title='Beer Style',
        yaxis_title='Average Rating Score',
        xaxis_tickangle=-45,  
        legend_title='Country',
        template='plotly_white',
        margin={'t': 50, 'b': 100, 'r': 50, 'l': 50}, 
    )

    # Displaying the plot
    #fig.show()

    return fig

####  Fun fact #2 - Bob travels from UK to Belgium

# Defining a function to prepare the dataframe used to plot average beer rating by year and Beer Name (funfact2)
def df_funfact_2(beers_df_copy):
    """
    Analyze beer ratings in Belgium over time and identify consistently rated beers.
    This function processes a DataFrame to extract beer data for Belgium and 
    analyzes ratings by year. It identifies beers that have been consistently 
    rated across all years in the dataset and calculates the average ratings 
    for these beers by year.

    Parameters:
    ----------
    beers_df_copy : pandas.DataFrame
        A DataFrame containing beer data.

    Returns:
    -------
    tuple
        - belgium_beers (pandas.DataFrame): A DataFrame containing beer data 
          filtered for Belgium with additional columns for 'year' and 'month'.
        - rating_by_year_beer_filtered (pandas.DataFrame): A DataFrame 
          containing average ratings by year for beers that have been rated 
          consistently across all years in the dataset.
    """
    # Filtering rows where `country_brewery` is 'Belgium'
    belgium_beers = beers_df_copy[beers_df_copy['country_user'] == 'Belgium'].copy()

    # Ensuring the 'date' column is in datetime format and extract the year
    belgium_beers['date'] = pd.to_datetime(belgium_beers['date'], errors='coerce')
    belgium_beers['year'] = belgium_beers['date'].dt.year
    belgium_beers['month'] = belgium_beers['date'].dt.month

    # Grouping by both 'year' and 'beer_name' and calculate the average rating
    rating_by_year_beer = belgium_beers.groupby(['year', 'beer_name'])['rating'].mean().reset_index()

    # Filtering beers that exist in all years
    # Finding all years in the dataset
    all_years = set(rating_by_year_beer['year'])

    # Identifying beers with entries in all years
    beers_with_all_years = rating_by_year_beer.groupby('beer_name')['year'].apply(set)
    beers_with_all_years = beers_with_all_years[beers_with_all_years.apply(lambda x: x == all_years)].index

    # Filtering the DataFrame to include only these beers
    rating_by_year_beer_filtered = rating_by_year_beer[rating_by_year_beer['beer_name'].isin(beers_with_all_years)]

    return belgium_beers, rating_by_year_beer_filtered


# Defining a function to create the plot for funfact_2
def plot_funfact_2(rating_by_year_beer_filtered):
    """
    Plot average beer ratings by year for consistently rated beers in Belgium.
    This function generates a line chart using Plotly to visualize the 
    year-over-year average ratings of some beers in Belgium. 

    Parameters:
    ----------
    rating_by_year_beer_filtered : pandas.DataFrame
        A DataFrame containing average ratings by year for beers that have 
        been consistently rated across all years. 

    Returns:
    -------
    None
        The function displays the Plotly line chart but does not return any value.
    """
    # Plotting a line chart using Plotly
    # Each line represents a beer, showing its average rating over the years
    fig = px.line(
        data_frame=rating_by_year_beer_filtered,
        x='year',
        y='rating',
        color='beer_name',
        markers=True,
        title='Average Beer Ratings by Year and Beer Name in Belgium',
        labels={
            'year': 'Year',
            'rating': 'Average Rating',
            'beer_name': 'Beer Name'
        }
    )

    # Enhancing chart appearance
    fig.update_layout(
        title={
            'text': 'Average Beer Ratings by Year and Beer Name in Belgium', 
            'x': 0.5,  
            'xanchor': 'center',  
            'yanchor': 'top', 
            'font': {'size': 20}
        },
        xaxis=dict(
            tickmode='linear',  
            tick0=min(rating_by_year_beer_filtered['year']), 
            dtick=1  
        ),
        yaxis=dict(title='Average Rating'),
        legend_title=dict(text='Beer Name'),
        template='plotly_white',  
        title_font=dict(size=20),
        legend=dict(
            title='Beer Name',
            x=1.05,  
            y=1
        )
    )

    # Displaying the plot
    #fig.show()

    return fig

# Defining a function to print the best beer names in winter and summer seasons (funfact2)
def best_beer_by_season(belgium_beers):
    """
    Identify the highest-rated beers in Belgium for winter and summer seasons.
    This function analyzes Belgian beer data to determine the beer with the 
    highest average rating for the winter and summer seasons.

    Parameters:
    ----------
    belgium_beers : pandas.DataFrame
        A DataFrame containing Belgian beer data.

    Returns:
    -------
    tuple
        - winter_highest_rated (pandas.Series): A Series representing the beer 
          with the highest average rating in the winter season.
        - summer_highest_rated (pandas.Series): A Series representing the beer 
          with the highest average rating in the summer season.
    """
    # Defining winter and summer months
    winter_months = [12, 1, 2]  # December, January, February
    summer_months = [6, 7, 8]   # June, July, August

    # Creating a new column to indicate the season
    belgium_beers['season'] = belgium_beers['month'].apply(lambda x: 'Winter' if x in winter_months else ('Summer' if x in summer_months else 'Other'))

    # Filtering for winter and summer data
    winter_data = belgium_beers[belgium_beers['season'] == 'Winter']
    summer_data = belgium_beers[belgium_beers['season'] == 'Summer']

    # Grouping by beer_name and calculate the average rating for each beer in winter and summer
    winter_avg_ratings = winter_data.groupby('beer_name')['rating'].mean().reset_index()
    summer_avg_ratings = summer_data.groupby('beer_name')['rating'].mean().reset_index()

    # Finding the beer with the highest average rating in each season
    winter_highest_rated = winter_avg_ratings.loc[winter_avg_ratings['rating'].idxmax()]
    summer_highest_rated = summer_avg_ratings.loc[summer_avg_ratings['rating'].idxmax()]

    return winter_highest_rated, summer_highest_rated

####  Fun fact #3 - Bob travels from Belgium to Canada 

# Defining a function to prepare the dataframe used to plot beer styles in Belgium and Canada (funfact3)
def df_funfact_3(beers_df_copy):
    """
    Analyze beer ratings for Belgium and Canada by style category.
    This function filters the dataset to include only beers from Belgium 
    and Canada.

    Parameters:
    ----------
    beers_df_copy : pandas.DataFrame
        A DataFrame containing beer data.
        
    Returns:
    -------
    tuple
        - beer_avg_rating (pandas.DataFrame): A DataFrame containing the average 
          ratings of each beer style category for both Belgium and Canada.
        - belgium_data (pandas.DataFrame): A DataFrame containing the average 
          ratings of each beer style category specific to Belgium.
        - canada_data (pandas.DataFrame): A DataFrame containing the average 
          ratings of each beer style category specific to Canada.
    """
    # Filtering data for Belgium and Canada
    filtered_data_belg_can= beers_df_copy[beers_df_copy['country_user'].isin(['Belgium', 'Canada'])]

    # Grouping by beer_name and country, calculate the average rating
    beer_avg_rating = (
        filtered_data_belg_can.groupby(['style_category', 'country_user'])['rating']
        .mean()
        .reset_index()
    )

    # Belgium data
    belgium_data = beer_avg_rating[beer_avg_rating['country_user'] == 'Belgium']

    # Canada data
    canada_data = beer_avg_rating[beer_avg_rating['country_user'] == 'Canada']

    return beer_avg_rating, belgium_data, canada_data

# Defining a function to create the plot for funfact_3
def plot_funfact_3(beer_avg_rating, belgium_data, canada_data):
    """
    Create a dual pie chart to compare beer styles and their average ratings in Belgium and Canada.
    This function shows the distribution of beer styles by their average 
    ratings. 

    Parameters:
    ----------
    beer_avg_rating : pandas.DataFrame
        A DataFrame containing beer styles and their average ratings for both 
        Belgium and Canada.
    belgium_data : pandas.DataFrame
        A DataFrame containing beer styles and their average ratings for Belgium only.
    canada_data : pandas.DataFrame
        A DataFrame containing beer styles and their average ratings for Canada only.

    Returns:
    -------
    None
        Displays an interactive plotly chart comparing Belgium and Canada beer styles.
    """
    # Generating a color palette with exactly 16 distinct colors
    unique_styles = beer_avg_rating['style_category'].unique()
    num_styles = len(unique_styles)
    color_palette = sns.color_palette("tab20", num_styles).as_hex()  # Convert to HEX for Plotly

    # Creating a color map for style categories
    color_map = {style: color for style, color in zip(unique_styles, color_palette)}

    # Mapping colors to Belgium and Canada beer styles based on the color_map
    belgium_colors = [color_map[style] for style in belgium_data['style_category']]
    canada_colors = [color_map[style] for style in canada_data['style_category']]

    # Initializing a Plotly figure
    fig = go.Figure()

    # Adding Belgium pie chart
    fig.add_trace(go.Pie(
        labels=belgium_data['style_category'],
        values=belgium_data['rating'],
        marker=dict(colors=belgium_colors),
        name="Belgium",
        textinfo='label+percent',
        textposition='inside',
        insidetextorientation='radial',
        hole=0.3 
    ))

    # Adding Canada pie chart
    fig.add_trace(go.Pie(
        labels=canada_data['style_category'],
        values=canada_data['rating'],
        marker=dict(colors=canada_colors),
        name="Canada",
        textinfo='label+percent',
        textposition='inside',
        insidetextorientation='radial',
        hole=0.3,   
        domain=dict(x=[0.55, 1]) 
    ))

    # Customizing the layout of the plot
    fig.update_layout(
        title="Beer styles in Belgium and Canada (Based on Average Ratings)",
        title_x=0.5,  
        grid=dict(columns=2, rows=1),  
        annotations=[
            dict(
                text='<b>Belgium</b>',  
                x=0.20,
                y=1.1, 
                font=dict(size=15, family="Arial", color="black"),
                showarrow=False
            ),
            dict(
                text='<b>Canada</b>', 
                x=0.80,
                y=1.1, 
                font=dict(size=15, family="Arial", color="black"),
                showarrow=False
            )
        ],
        legend=dict(
            x=1.05,  
            y=0.5,
            traceorder="normal",
            font=dict(size=12),
        ),
        piecolorway=color_palette,
        showlegend=True, 
        height=500,  
        width=1100, 
    )

    # Displaying the figure
    #fig.show()

    return fig

#### Fun fact #4 - Bob travels from Canada to the USA

# Defining a function to prepare the dataframe used to plot the heatmap (funfact4)
def df_funfact_4(beers_df_copy): 
    """
    Analyze beer ratings for breweries in the United States by state.
    This function filters the dataset to include only beers from the United States,
    calculates the average rating for each state, and sorts the states by their
    average ratings in descending order.

    Parameters:
    ----------
    beers_df_copy : pandas.DataFrame
        A DataFrame containing beer data.

    Returns:
    -------
    tuple
        - us_data (pandas.DataFrame): A DataFrame containing beer data specific 
          to the United States.
        - state_avg_ratings (pandas.DataFrame): A DataFrame containing the average 
          ratings for each state in the United States, sorted in descending order.
    """   
    # Filtering data for US breweries
    us_data = beers_df_copy[beers_df_copy['country_user'] == 'United States']

    # Grouping by 'state_user' and calculating the average rating for each state
    state_avg_ratings = us_data.groupby('state_user')['rating'].mean().reset_index()

    # Sorting the states by average rating
    state_avg_ratings = state_avg_ratings.sort_values(by='rating', ascending=False)

    return us_data, state_avg_ratings

# Defining a function to prepare the dataframe used to plot the most popular brewery per state (funfact4_v2)  
def df_funfact_4_brewery(us_data):
    """
    Prepare a DataFrame showing the most popular brewery in each state based on the number of entries.
    This function calculates the brewery with the highest count of entries (popularity) 
    in each state from the provided U.S beer data.

    Parameters:
    ----------
    us_data : pandas.DataFrame
        A DataFrame containing beer data specific to the United States. 

    Returns:
    -------
    pandas.DataFrame
        A DataFrame containing the most popular brewery for each state.
    """
    # Calculating most popular brewery by state
    popular_breweries = us_data.groupby(['state_brewery', 'brewery_name']).size().reset_index(name='count')
    most_popular_brewery = popular_breweries.loc[popular_breweries.groupby('state_brewery')['count'].idxmax()]

    # Merging the results into a single DataFrame
    return most_popular_brewery[['state_brewery', 'brewery_name', 'count']].rename(columns={'brewery_name': 'most_popular_brewery', 'count': 'brewery_count'})


# Defining a function to create the plot for funfact_4_v2 concerning breweries
def plot_funfact_4_brewery(most_popular_brewery):
    """
    Create a bar chart to visualize the most popular brewery in each state.
    The bar chart shows the brewery with the highest number of entries for each state 
    along with the count. 

    Parameters:
    ----------
    most_popular_brewery : pandas.DataFrame
        A DataFrame containing the most popular brewery per state.

    Returns:
    -------
    None
        The function displays the bar chart using Plotly.
    """
    # Generating unique colors for each brewery
    unique_breweries = most_popular_brewery['most_popular_brewery'].unique()
    num_breweries = len(unique_breweries)

    # Creating a continuous colormap and convert it to discrete values
    colors = px.colors.sample_colorscale('turbo', [i / num_breweries for i in range(num_breweries)])
    brewery_color_map = {brewery: colors[i] for i, brewery in enumerate(unique_breweries)}

    # Adding custom data (brewery names) for hover template
    most_popular_brewery['hover_brewery'] = most_popular_brewery['most_popular_brewery']

    # Creating the bar chart using Plotly
    fig = px.bar(
        most_popular_brewery,
        x='state_brewery',
        y='brewery_count',
        color='most_popular_brewery',
        labels={'state_brewery': 'State', 'brewery_count': 'Count'},
        title="Most Popular Brewery per State",
        color_discrete_map=brewery_color_map, 
        custom_data=['hover_brewery']  
    )

    # Updating layout for better visualization
    fig.update_layout(
        title_x=0.5,  
        xaxis=dict(
            title="State",
            tickmode='linear',  
            tickangle=45,  
        ),
        yaxis=dict(title="Brewery Count"),
        legend_title_text='Brewery Name',
        height=600,
        width=1000,
        margin=dict(l=50, r=50, t=50, b=100)  
    )

    # Adding hover template for detailed tooltips
    fig.update_traces(
        hovertemplate='<b>State:</b> %{x}<br>' +
                    '<b>Brewery:</b> %{customdata[0]}<br>' +
                    '<b>Count:</b> %{y}<extra></extra>'
    )

    # Displaying the figure
    #fig.show()

    return fig


# Defining a function to save figures as html format
def save_plot_as_html(fig, save_path):
    """
    Save a Plotly figure as an HTML file.

    Parameters:
    ----------
    fig : plotly.graph_objects.Figure
        The Plotly figure to save.
    save_path : str
        The file path where the HTML file will be saved.

    Returns:
    -------
    None
        The function saves the HTML file and does not return any value.
    """
    pio.write_html(fig, save_path)

# Defining a function to save figures as svg format
def save_plot_as_svg(fig, save_path):
    """
    Save a Plotly figure as an SVG file.

    Parameters:
    ----------
    fig : plotly.graph_objects.Figure
        The Plotly figure to save.
    save_path : str
        The file path where the SVG file will be saved.
    
    Returns:
    -------
    None
        The function saves the SVG file and does not return any value.
    """

    pio.write_image(fig, save_path, format='svg')
