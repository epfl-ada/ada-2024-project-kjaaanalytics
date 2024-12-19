---
layout: analysis
title: "Climate-related Analysis"
subtitle: ""
previous: /storyline/funfact-4
next: /storyline/conclusion 
permalink:  /storyline/climate-related-analysis
---

After leaving the freezing country of Canada, Bob arrives in Arizona . After looking at the polarizing beers there, it would be interesting to analyze the staple beers, or crowd-favorites, this time in the USA. This would allow identifying general trends and preferences rather than extremes reviews. Additionally, linking those general trends to see wether or not they are linked to climate would be an interesting insight for Bob!

In order to observe a meaningful relationship, we must define the concept of “climate” in a quantifiable manner.  Using refined weather data (monthly mean temperature and precipitation), each point is clustered with similar samples using a Kmean algorithm, as to produce 5 typical climate for the USA. To choose the appropriate number of clusters n, the algorithm is ran with different with values for n going from 2 to 9. The visual inspection of the MSE score on the data indicates that n = 5 is a reasonable choice, as it is a good compromise between clustering accuracy and meaningful generalized typical climate for the remaining analysis.

<!-- Plot goes here -->
<img src="{{ 'assets/figures/analysis4_plot.png' | relative_url }}" width="1000">

The results from the clustering are interesting as they reflect well both the latitude differences and the topography. The north-south stratification is expected from northern states being colder and rainier than the southern states and is easily discernable. The topography appears with the blue trail on the west coast situated where the Rocky Mountains are.

These clustered samples are subsequently interpolated per state, using majority voting to obtain the map in the bottom left. This map shows the most representative *typical climate* per state.

To relate those climatic features to beer preferences, and thus discover what are the best-rated styles in each *typical climate*, American overall beer ratings are grouped by state and by beer style, keeping the average overall rating per style.  Each style is then ranked per state, and the favorite style per state is kept. Using majority voting again, each climatic cluster obtains a best-rated beer style, supposedly representing the favorite style for this *typical climate.*

The map on the lower right displays this favorite beer style. It shows that out of 5 typical climates, three of them most like the *Quadrupel* style. The northern states rate best the *India Pale ALE (IPA)* and the coastal states prefer *American Double / Imperial IPA.*

Strong from this new knowledge about the link between climate and beer preferences, Bob wonders to what *typical climate* Lausanne belongs. If only he knew, he could recommend the best-rated style to his friends at *Satellite*!