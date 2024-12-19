---
layout: analysis
title: "Semantic Analysis"
subtitle: ""
previous: /storyline/funfact-1
next: /storyline/funfact-2
permalink:  /storyline/semantic-analysis
---

Bob arrives in New Castle, the city with the most breweries in England ! He has learned the differences between English and Swiss preferences. But, he still does not know how to properly describe a beer, based on its style. He wants to learn about how to BEST describe them.


To help Bob hone his skills in beer descriptions we plot a word cloud depending on the type of beer he wants to describe. The data has been preprocessed, removing key stop words as well as special characters.

<div>
    {%- include dropdown_plot.html content="wordcloud_categories" -%}
</div>

Bob knows that Stout and Porter beers are the most appreciated in England. He can know describe them like a connoiseur. For example, to describe Stout, he can say that the beer is light, sweet and that it tastes like dark chocolate ! 

Now that he knows how to describe beer styles properly, he is ready to go on a new adventure to discover the seasonality of beers preference. What better way to discover that than going one of the biggest beer festival in the capital of beer : _Brussels_ !
