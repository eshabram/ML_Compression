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

# data retreived from https://www.kaggle.com/datasets/rtatman/english-word-frequency?resource=download
df = pd.read_csv('unigram_freq.csv')

#%%
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

        
def encode_number(num, bits, bit_code):
    bits = [8, 16, 24, 32]
    bit_code = ['00', '01', '10', '11']
    bin_num = format(num, 'b')
    # Calculate the number of bytes required
    num_bytes = (len(bin_num) + 7) // 8
    # Pad to fit the byte size
    bin_num = bin_num.zfill(num_bytes * 8)
    
    encoded = ""
    
    # Determine the bit code prefix for the given number of bytes
    prefix = bit_code[num_bytes - 1]
    
    # Add the prefix to the beginning and then append the binary number
    encoded = prefix + bin_num

    return encoded


#%%
animation_event = threading.Event()
animation_thread = threading.Thread(target=loading_animation)
animation_thread.start()

df['key'] = df.index.map(lambda x: encode_number(x, bits, bit_code))



animation_event.set()
animation_thread.join()

#%%
def encode(message):
    tokens = nltk.word_tokenize(message.lower())
    # Filter out punctuation
    tokens = [token for token in tokens if token not in string.punctuation]
    binary_encode = ''
    for token in tokens:    
        binary_encode += str(df.loc[df['word'] == token, 'key'].iloc[0])

    return binary_encode

message = "I like to eat chicken!"
print(encode(message))
print(len(message))


    
