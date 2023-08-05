#%%
import pandas as pd
import numpy as np
import os
import sys
import time
import string
import threading
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import nltk
import threading
import time
nltk.download('punkt')
from collections import Counter

def loading_animation():
    cursor_anim = '|/-\\'
    i = 0
    while not animation_event.is_set():
        cursor = cursor_anim[i % len(cursor_anim)]
        with threadlocker:
            sys.stdout.write(f"\rWorking {cursor}    ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
        
threadlocker = threading.Lock()
#%%
# open file and tokenize words
tokens = []
with open('data.txt', 'r') as f:
    # Start the animation thread
    animation_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()
    for line in f:
        tokens.extend(nltk.word_tokenize(line))
    # Start the animation thread
    animation_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()
#%%
# Filter out punctuation
tokens = [token for token in tokens if token not in string.punctuation]

#join animation thread
animation_event.set()
animation_thread.join()
#%%
# Count frequency of each word
word_counts = Counter(tokens)
print(word_counts)
#%%
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


#%%
# Define the encoder
class Encoder(nn.Module):
    def __init__(self, input_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()
        self.hid_dim = hid_dim
        self.n_layers = n_layers
        self.embedding = nn.Embedding(input_dim, emb_dim)
        self.rnn = nn.LSTM(emb_dim, hid_dim, n_layers, dropout=dropout)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src):
        embedded = self.dropout(self.embedding(src))
        outputs, (hidden, cell) = self.rnn(embedded)
        return hidden, cell

# Define the decoder
class Decoder(nn.Module):
    def __init__(self, output_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()
        self.output_dim = output_dim
        self.hid_dim = hid_dim
        self.n_layers = n_layers
        self.embedding = nn.Embedding(output_dim, emb_dim)
        self.rnn = nn.LSTM(emb_dim, hid_dim, n_layers, dropout=dropout)
        self.fc_out = nn.Linear(hid_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input, hidden, cell):
        input = input.unsqueeze(0)
        embedded = self.dropout(self.embedding(input))
        output, (hidden, cell) = self.rnn(embedded, (hidden, cell))
        prediction = self.fc_out(output.squeeze(0))
        return prediction, hidden, cell

# Define the seq2seq model
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = trg.shape[1]
        trg_len = trg.shape[0]
        trg_vocab_size = self.decoder.output_dim
        outputs = torch.zeros(trg

