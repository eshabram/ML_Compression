from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import string
import re

# Function to preprocess text
def preprocess_text(text):
    # Removing emojis
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    # Tokenize and convert to lower case
    words = word_tokenize(text.lower())

    # Remove punctuation
    words = [word for word in words if word.isalnum()]

    return words

# Assume we have a text file 'sample.txt'
with open('sample.txt', 'r') as f:
    text = f.read()

tokens = preprocess_text(text)

# Create Word2Vec model
model = Word2Vec([tokens], min_count=1)

# Save the model for later use
model.save('word2vec_model')

# Load the model
model = Word2Vec.load('word2vec_model')

# Function to encode sentence
def encode_sentence(sentence, model):
    return [model.wv[word] for word in preprocess_text(sentence)]

# Function to decode sentence
def decode_sentence(encoded_sentence, model):
    return [model.wv.most_similar([vector], topn=1)[0][0] for vector in encoded_sentence]

# Let's try encoding and decoding a sentence
sentence = "Hello, world!"
encoded = encode_sentence(sentence, model)
decoded = decode_sentence(encoded, model)
print("Original:", sentence)
print("Decoded:", " ".join(decoded))
