---
layout: analysis
title: "Semantic Analysis"
subtitle: ""
previous: /storyline/funfact-1
next: /storyline/funfact-2
permalink:  /storyline/semantic-analysis
---

Bob arrives in New Castle, the city with the most breweries in England! He has learned the differences between English and Swiss preferences. But, he still does not know how to properly describe a beer, based on its style. He wants to learn about how to BEST describe them.  

To help Bob hone his skills in beer descriptions we plot a word cloud depending on the type of beer he wants to describe. The data has been preprocessed, removing key stop-words as well as special characters.  The data was chosen in England because most of the users write comments in English, so the word cloud will be unbiased towards other languages. Furthermore, word clouds display words based on their frequency. If a word appears a lot in the textual reviews, it will appear bigger.

<div>
    {%- include dropdown_plot.html content="wordcloud_categories" -%}
</div>

Bob knows that Stout and Porter beers are the most appreciated in England. He can know describe them like a connoiseur. For example, to describe Stout, he can say that the beer is light, sweet and that it tastes like dark chocolate! He also wonders how the word descriptions can change throughout the year. To help him, we plotted the word clouds according to the seasons for all types of beers !

<div style="align-self: center">
<img alt="Seasonality Analysis" src="{{'/assets/figures/word_clouds_seasons.svg' | relative_url}}" width="650">
</div>

Semantics do not seem to change much through the year. However, could it be that preferences shift according to the seasons?  For example, we can see that sweet, dry and bitter are used all year long.  

Follow along as Bob goes on a new adventure to discover the seasonality of beers preference. What better way to discover that than going to one of the biggest beer festivals in the capital of beer : _Brussels_!
