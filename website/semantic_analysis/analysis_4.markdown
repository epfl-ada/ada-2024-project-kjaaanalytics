---
layout: analysis
title: "Semantic Analysis #4"
subtitle: "Arizona (Not the Tea....The State please)"
previous: /storyline/funfact-4
next: /storyline/end
permalink:  /storyline/analysis-4
---

After leaving the freezing country of Canada, Bob arrives in Arizona. … .We help Bob identify popular style in different climate. 

First, we cluster each loacalization of the us based on climate similarities to find 5 *typical climates*. Then, each states is assigned a *typical climate* based on majority voting

## Did You Know?
Amélie made this amazing plot! I love it ❤

<div>
    {% include interactive_beer_mapping.html %} 
</div>

## Explainations
ADD 1-2 SENTENCES INTRO

In order to observe a meaningful relationship, we must define the concept of “climate” in a quantifiable manner.  Using refined weather data (monthly mean temperature and precipitation), each point is clustered with similar samples, as to produce 5 typical climate for the USA. To choose the appropriate number of clusters n, the algorithm is ran with different with values for n going from 2 to 9. The visual inspection of the MSE score on the data indicates that n = 5 is a reasonable choice, as it is a good compromise between clustering accuracy and meaningful generalized typical climate for the remaining analysis.

<img title="" alt="plot analysis 2" src="/assets/figures/analysis4_plot.svg">

The results from the clustering are interesting as they reflect well both the latitude differences and the topography. The north-south stratification is expected from northern states being colder and rainier than the southern states and is easily discernable. The topography appears with the blue trail on the west coast situated where the Rocky Mountains are.

These clustered samples are subsequently interpolated per state, using majority voting to obtain the map in the bottom left.

To relate those climatic feature to beer preferences, and thus discovering what are the best rated styles in each *typical climate*, american overall beer ratings are grouped by states and by beer style, keeping the average overall rating per style.  Each style is then ranked per state, and the favorite style per state is kept. Using majority voting again, each climatic cluster obtains a best-rated beer style, supposedly representing the favorite style for this *typical climate.*

The map on the lower right displays this favorite beer style. It shows that out of 5 typical climates, three of them most like the *Quadrupel* style. The northern states rate best the *India Pale ALE (IPA)* and the coastal states prefer *American Double / Imperial IPA.*

Strong from this new knowledge about the link between climate and beer preferences, Bob wonders to what *typical climate* Lausanne belongs. If only he knew, he could recommend the best-rated style to his friends at *Satellite*!