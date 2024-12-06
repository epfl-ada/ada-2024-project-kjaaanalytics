---
layout: story
title: "Fun Fact: Beer Popularity"
subtitle: "Exploring the most-loved beers in different countries"
previous: /
next: /storyline/analysis-uk
permalink: /storyline/funfact-1/
---


## Did You Know?
The highest-rated beer in the world is a Belgian Quadrupel!


<script>
    document.querySelectorAll('.nav-button').forEach(button => {
    button.addEventListener('click', event => {
        event.preventDefault();
        const href = event.target.getAttribute('href');
        document.body.style.opacity = '0';
        setTimeout(() => {
        window.location.href = href;
        }, 1000);
    });
    });
    window.onload = () => {
    document.body.style.transition = 'opacity 1s';
    document.body.style.opacity = '1';
    };
</script>