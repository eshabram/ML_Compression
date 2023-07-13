import nltk
import praw
import pandas as pd
import os
import sys
import time
import string
import threading
from collections import Counter


reddit = praw.Reddit(client_id='uHEfoWv1Jp1dCT3Ff2gF4A' \
                               , client_secret='hD6U0U74B9iuSpFbp_dNqHFVhXVFhQ', \
                                user_agent='ML_compression_v1', check_for_async=False)

pop = reddit.subreddits.popular(limit=50)

for sub in pop:
    print(sub.display_name)
    
# Tokenize text into words
tokens = nltk.word_tokenize(text)

# Filter out punctuation
tokens = [token for token in tokens if token not in string.punctuation]

# Count frequency of each word
word_counts = Counter(tokens)

# Convert to DataFrame
df = pd.DataFrame.from_dict(word_counts, orient='index').reset_index()
df = df.rename(columns={'index':'word', 0:'count'})

# Add word length as a column
df['length'] = df['word'].apply(len)

# Calculate score as frequency divided by length
df['score'] = df['count'] / df['length']

# Sort by score
df = df.sort_values(by='score', ascending=False)

# Assign codes
ascii_chars = list(string.printable)
df['code'] = [ascii_chars[i] if i < len(ascii_chars) else word for i, word in enumerate(df['word'])]

# Print the DataFrame
print(df)
