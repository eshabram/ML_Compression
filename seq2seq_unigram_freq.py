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

bits = [8, 16, 24, 32]
bit_code = ['00', '01', '10', '11']
threadlocker = threading.Lock()
animation_event = threading.Event()
animation_thread = threading.Thread(target=loading_animation)
#%%        
def encode_number(num, bits, bit_code):
    # used in building the column 'keys' with custom scheme
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


def assign_keys(bits, bit_code):
    # assign key values with custom scheme, based on the index of a word.
    # Index = rank. Keys are shorter for more common words.
    animation_thread.start()
    df['key'] = df.index.map(lambda x: encode_number(x, bits, bit_code))
    animation_event.set()
    animation_thread.join()


def binary_encode(message):
    # This function does the encoding of messages in our custom binary format.
    # the format is read from left to right, where the first two bits are one of
    # four combinations indicating whether there are more bytes to be read after 
    # the first byte. 00 indicates just the first byte, 01 indicates that there 
    # are two bytes to be read in. Once those bytes have been read, the next code
    # is given, and the process repeats. 
    
    tokens = nltk.word_tokenize(message.lower())
    
    # Filter out punctuation
    tokens = [token for token in tokens if token not in string.punctuation]
    binary_encode = ''
    
    # locate the index of a given word, and add it to the scheme
    for token in tokens:    
        binary_encode += str(df.loc[df['word'] == token, 'key'].iloc[0])

    return binary_encode


def decode_sequence(sequence):
    # This is the main function used for decoding. 
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 4}
    idx = 0
    indices = []

    while idx < len(sequence):
        # Extract the bit code
        bit_code = sequence[idx:idx+2]
        idx += 2

        # Determine the number of bytes to read based on the bit code
        num_bytes = bit_code_to_bytes[bit_code]

        # Read the number and convert to integer
        num_str = ''
        for _ in range(num_bytes):
            if len(sequence) - idx < 8:
                break
            num_str += sequence[idx:idx+8]
            idx += 8
        if num_str:
            indices.append(int(num_str, 2))
    print(indices) 
    # rebuild string (simple version)
    message = ''
    for idx in indices:
        if len(message) == 0:
            message += get_word(idx)
        else:
            message += ' ' + get_word (idx)
            
    return message


def get_word(idx):
    # this method simply return the word given an index
    return df['word'][idx]

    
#%%
assign_keys(bits, bit_code)
#message = "I like to eat chicken!"
#print(binary_encode(message))
#print(len(message))


    
