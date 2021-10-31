import discord
import pandas as pd
import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.util import flatten, ngrams, bigrams, trigrams
from collections import Counter
from nltk.probability import FreqDist
import string
from nltk.stem import WordNetLemmatizer
import time
from datetime import datetime

# Need permission to read history on channel, use channel ID
client = discord.Client()
# CHANNEL = 899799560317198350    # personal server
CHANNEL = 892274233198129202     # mice-alpha
# CHANNEL = 888113560666927147  # general
LAST_RAN_FILENAME = 'last_message.txt'

# words to filter out (added a bunch of random ones that seemed unimportant, can add more based on results)
stop_words = set(stopwords.words('english'))
stop_words.update(['tbh', 'eth', 'keep', 'telling', 'tbh', 'give', 'lot', 'like', 'go', 'oh','whats', 'could', 'dont', 'people', 'guys', 'know', 'alpha', 'need', 'right', 'u', 'would', 'sure', 'really', 'also', 'anyone', 'much', 'looks', 'well', 'os', 'already', 'even', 'many', 'shit', 'first', 'matthew888928579583361036', 'haroldcringe827253907516293210', 'agm881563069338234992', 'gmgm', 'wtf', 'true', 'idk', 'hmm', 'well' 'alpha', 'yep', 'yes', 'nice', 'wow', 'thanks', 'link', 'lmao', 'haha', 'hahaha', 'matthewsmoke888928579210067988', 'damn', 'one', 'get', 'lol', 'think', 'got', 'im', 'yeah', '’', 'still', 'going', 'see', 'thats', 'na', 'yea', 'morning', 'gm'])


@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL)
    
    # If we ran before we can get the last message we saw and read after that
    # This part isn't working right now. Have tried both times and now Message objects.
    # Works on my personal server but not Mice for some reason
    # Relevant docs: https://discordpy.readthedocs.io/en/stable/api.html#messageable
    try:
        limit = None
        with open(LAST_RAN_FILENAME, 'rb') as infile:
            lastMSG = pickle.load(infile)
    # If we did not run before then just get last N messages
    except:
        limit = 4000
        lastMSG = None

    # Getting messages
    messages = await channel.history(limit=limit, oldest_first=False, after=lastMSG).flatten()
    print(f'Data from latest {limit} messages. All times local.\nOldest: {utc2local(messages[-1].created_at)}, Newest: {utc2local(messages[0].created_at)}')

    # Isolating actual message content
    message_contents = [message.content for message in messages]
    process_messages(message_contents)

    # Save last message from list
    lastMSG = messages[-1]
    with open(LAST_RAN_FILENAME, 'wb') as outfile:
        pickle.dump(lastMSG, outfile)

    print('Closing...')
    await client.close()

def process_messages(messages):
    # Supposed to reduce words to stems (https://www.geeksforgeeks.org/python-lemmatization-with-nltk/)
    lemmatizer = WordNetLemmatizer()

    # Remove punctuation, make all lowercase, break msgs into individual words, lemmatize
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table).lower() for w in messages]
    nltk_tokens = [word_tokenize(message) for message in stripped]
    flatten_list = [j for sub in nltk_tokens for j in sub if j not in stop_words]
    lemmas = [lemmatizer.lemmatize(word) for word in flatten_list]

    # Getting word frequency of top N words
    dist = FreqDist(lemmas)
    top_n_single = 100
    print('TOP INDIVIDUAL WORD')
    for mc in dist.most_common(top_n_single):
        print(mc)


    # Most common 2, 3 word pairs
    top_n_bigrams = 20
    print('BI-GRAMS')
    print(FreqDist(list(bigrams(lemmas))).most_common(top_n_bigrams))
    print('TRI-GRAMS')
    print(FreqDist(list(trigrams(lemmas))).most_common(top_n_bigrams))

    # Not sure bout this part yet
    #creating a dictionary that shows occurances of n-grams in text
    # n_gram = 5 
    # n_gram_dic = dict(Counter(ngrams(flatten_list, n_gram)))
    # print(n_gram_dic)

def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset

client.run('ASK_ME_FOR_TOKEN')