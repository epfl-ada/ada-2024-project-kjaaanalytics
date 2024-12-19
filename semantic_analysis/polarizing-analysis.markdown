---
layout: analysis
title: "Polarizing Beer Analysis"
subtitle: ""
previous: /storyline/funfact-3
next: /storyline/funfact-4
permalink:  /storyline/polarizing-analysis
---

Bob liked the friendliness of belgian people so he goes to Canada to test the friendliness of canadians :). However, he wants to learn more about Canadian beer preferences. Do Canadian also rate beers  more nicely or if do they tend to like more polarizing beers. 

First, let’s look at the distribution of the ratings for the canadian users.

<img alt="Polarizing analysis plot" src="{{'/assets/figures/canada_beer_distributions.svg' | relative_url}}" width="1000">

## So, which beers are the most polarizing then?

Next, he’ll take a closer look at the distribution of ratings from Canadian users to uncover those polarizing beers. This will help him identify which beers have strong opinions—whether they’re loved by some and hated by others—giving him even more insight into the local beer culture.

To help Bob understand the distribution of beers, we plot it with the threshold that we set for the liked and disliked beers which are 1 sigma above and 1 sigma below the mean beer rating. We also set a polarizing threshold, that is defined as a standard deviation of ratings in the 90th percentile of all beer rating standard deviations. This will allow Bob to better understand how polarizing beers are rated!

<img alt="Top 5 Beers in Canada" src="{{'/assets/figures/Top_5_Polarizing_Beers_in_Canada.svg' | relative_url}}" width="650">

Bob realizes that the beer attributes vary significantly, which likely contributes to their polarizing nature. For example, taste, appearance and aroma appear to be the most varied attributes among the beers. This makes sense as these elements are highly subjective and prone to divisive opinions. However, most of the beers have similar scores for palate, suggesting that this attribute contributes less to their polarizing ratings. It might indicate that drinkers generally agree on palate but diverge on other sensory attributes.

Bob feels he has learned a lot about Canadian preferences. Multiple factors could influence the preferences for beer styles. This got Bob wondering, how can climate affect the preferences of beers? To answer this question, he will head to the United States, a country that has various climates across the whole country.