import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import nltk
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
import string


"""
Preprocesses the input text by performing the following steps:
1. Converts the text to a string if it is not already.
2. Removes punctuation.
3. Converts all text to lowercase.
4. Tokenizes the text.
5. Removes stop words and stems the remaining words.

Parameters:
text (str): The input text to be preprocessed.

Returns:
list: A list of processed tokens after removing stop words and stemming.

TODO: Convert all spcial characters to only alphabet characters. Ask chatGPT for the regex command.
"""
def preprocess_text(text):
    
    # Convert text to string if it is not already
    text = str(text)
    
    # Remove punctuation                                                 
    text = text.translate(str.maketrans(' ', ' ', string.punctuation))

    # Convert all text to lowercase 
    text = text.lower()   

    # Tokenize the text
    tokens = word_tokenize(text)                                     
    
    # Initialize a Porter stemmer for word stemming
    stemmer = PorterStemmer()

    # Define custom stop words to remove from the text
    CUSTOM_STOP_WORDS = {"'s",'s','note','notes','almost','beer','lots','quite','maybe','lot','though', 'aroma',
                  'flavor','palate','overall','appearance',"n't",'taste','head','mouthfeel','bottle','glass',
                  'little','smell','bit','one','lot','nose','really','much','body','hint','quot','spice','itâ s',
                  'good','great', 'nice','love','like','isnt','isn','isnâ','isnâ t','isn t','don','donâ','donâ t'}
    stopwords_set = set(stopwords.words('english')).union(CUSTOM_STOP_WORDS)
    
    # Remove stop words and stem the remaining words
    # TODO: Fix stemmer. Currently, stemming changes y'to i, which is not desired.
    # tokens = [stemmer.stem(token) for token in tokens if token not in stopwords_set]
    tokens = [token for token in tokens if token not in stopwords_set]
    filtered_text = ' '.join(tokens)
    return filtered_text


"""
Plots a simple word cloud of the input text.

Parameters:
text (list): A list of tokens to be visualized in the word cloud.

Returns:
None -- displays the word cloud plot.
"""
def plot_wordcloud(text):
    text_single_string = ' '.join(text)
    # Create and generate a word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white',colormap='viridis').generate(text_single_string)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')