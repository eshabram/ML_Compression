#%%
import pandas as pd
import numpy as np
import os
import sys
import time
import string
import threading
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import pdb

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


def binary_encode(message, args):
    # This function does the encoding of messages in our custom binary format.
    # the format is read from left to right, where the first two bits are one of
    # four combinations indicating whether there are more bytes to be read after 
    # the first byte. 00 indicates just the first byte, 01 indicates that there 
    # are two bytes to be read in. Once those bytes have been read, the next code
    # is given, and the process repeats. 
        
    tokens = nltk.word_tokenize(message)
    
    token_space_info = []  # This list will store tuples (token, space_before)
    
    last_end = 0  # this will keep track of where the last token ended
    
    for token in tokens:
        start = message.find(token, last_end)  # look for token occurrence after the last token
        space_before = False  # default is True, meaning we assume there's a space before
        if start > 0 and message[start - 1] != ' ' and token in string.punctuation:
            space_before = True
        token_space_info.append((token, space_before))
        last_end = start + len(token)  # update the last token's end
    
    print(token_space_info)
    if args.verbose:
        print(tokens)
    
    binary_encode = ''
    # locate the index of a given word
    for token, no_space_before in token_space_info:    
        append_bits = ''
        key = df.loc[df['word'] == token.lower(), 'key']
        # append bits for token attributes
        if not key.empty:
            if token.istitle():
                append_bits += '101'
            if no_space_before and token in string.punctuation:
                append_bits += '110'
            if token.isdigit():
                append_bits += '111'
            
            # handle the space before info, if required, using space_before variable

            append_bits += '0'
            if token.isdigit():
                return
            print(f'Key: {key}')
            binary_encode += (append_bits + str(key.iloc[0]))
        else:
            print(f"Warning: Token '{token}' not found in dataframe.")
            
    return binary_encode


def decode_sequence(sequence, args):
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 1}
    idx = 0
    words = []
    no_space = False

    while idx < len(sequence):
        attributes = []
        # Check for the presence of attributes
        while sequence[idx] == '1':
            #pdb.set_trace()

            # Extract the next two bits to determine the attribute type
            attribute_code = sequence[idx:idx+2]
            idx += 2
            
            if attribute_code == '10':
                attributes.append("capitalized")
            elif attribute_code == '11':
                attributes.append("no_space_punctuation")
                print(f'Attributes: {attributes}')
            # Add more attribute handling as needed...

        # After reading attributes, move past the '0' bit
        idx += 1

        # Extract the bit code to determine the bytes for the key
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
            if bit_code == '11':
                # Subtract the integer value of the byte from the length of df
                key_val = len(df) - int(num_str, 2) -1
            else:
                key_val = int(num_str, 2)
            #pdb.set_trace()
            # Retrieve word from dataframe based on the key
            word = get_word(key_val)
            
            # Handle attributes
            if "capitalized" in attributes:
                word = word.capitalize()
            
            if "no_space_punctuation" in attributes:
                no_space = True
                
            words.append(word)

            
    #pdb.set_trace()
    # Reconstruct the messages
    if no_space:
        message = ''.join(words)
    else:
        message = ' '.join(words)

    
    return message


def binary_encode_simple(message, args):
    # This function is the simple/light-weight version of the encoding scheme.
    # this version retains as much meaning as possible while keeping the 
    # compression down between 30% and 40%. It doesn't handle numbers well.
    
    # tokenize words and punctuation
    tokens = nltk.word_tokenize(message.lower())
    if args.verbose:
        print(tokens)
    # Filter out punctuation
    #tokens = [token for token in tokens if token not in string.punctuation]
    
    binary_encode = ''
    
    # locate the index of a given word, and add it to the scheme
    for token in tokens:    
        key = df.loc[df['word'] == token, 'key']
        if not key.empty:
            binary_encode += '1' + str(key.iloc[0])
        else:
            for letter in token:
                binary_encode += str(bin(ord(letter))[2:]).zfill(8)                
            if args.verbose:
                print(f"Warning: Token '{token}' not found in dataframe. Sending as ascii representation.")


    return binary_encode


def decode_sequence_simple(sequence, args):
    # This is the simple version of the main function used for decoding. 
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 1}
    idx = 0
    message = ''
    
    while idx < len(sequence) and len(sequence) - idx >= 8:
        if sequence[idx] == '1':
            idx += 1
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
                if bit_code == '11':
                    # Subtract the integer value of the byte from the length of df
                    index_value = len(df) - int(num_str, 2) -1
                else:
                    index_value = int(num_str, 2)
                    
            if len(message) == 0:
                message += get_word(index_value)
            else:
                message += ' ' + get_word(index_value)

        else:
            #pdb.set_trace()
            word = ''
            if len(message) != 0:
                message + ' '
            try:
                while sequence[idx] == '0':
                    ascii_code = int(sequence[idx:idx+8], 2)  # Convert the 8-bit code to an integer
                    ascii_character = chr(ascii_code)  # Convert the integer to the corresponding ASCII character
                    word += ascii_character      
                    idx += 8

            except IndexError:
                pass
            message  += word
    return message


def get_word(idx):
    # this method simply return the word given an index
    return df['word'][idx]

    
#%%
# assign key values with custom scheme, based on the index of a word.
# Index = rank. Keys are shorter for more common words.
animation_thread.start()
df['key'] = df.index.map(lambda x: encode_number(x, bits, bit_code))

"""
# this section of cade adds ascii to the end of df so that it can be used as
# a token.
# ASCII codes from 32 to 126
ascii_codes = list(range(32, 127))
ascii_chars = [chr(code) for code in ascii_codes]

# Generate keys for each ASCII character
keys = [f'11{format(i, "08b")}' for i in range(len(ascii_chars))][::-1]
animation_event.set()
animation_thread.join()

# Create a new dataframe with ASCII characters and their keys
ascii_df = pd.DataFrame({
    'word': ascii_chars,
    'key': keys
})

# Append the new dataframe to the original one
df = pd.concat([df, ascii_df], ignore_index=True)  
"""
animation_event.set()
animation_thread.join()



""" 
00 = 
01 = capital word
10 = no space before
11 = number (when read in, slpit larger numbers and send as multi number bytes.
             we can give 8 bits for each number, and split numbers bigger than 
             that to fit a byte by byte scheme)
   
11 1 10 0 00 00000001 -> (using this translation key with middle indicator bits,
                          would represent the number 1 with no space in front. 
                          This would work nice if number were more commonly used 
                          1-9 only, but with this scheme we can get much larger 
                          numbers up over 4 billion, but the real cool thing 
                          about it would be that if you used commas, then they 
                          wouldn't have to be that big.)
   
or

1 01 0 0000000001 -> (this would be a capital word.)
0 0000000001 -> (and this would be a lowercase, and we could reuse the other 00 
                  somewhere else. This would be efficient because capital words
                  are much less common, and the overhead is only 3 more bits to
                  achieve a capital word. It does however mean that each word 
                  will be 1 bit longer, making longer messages a bit larger.)
   
000 = word
001 = cap word
010 = word no space before
011 = cap word no space before
100 = number
101 = number no space before
110 =
111 = 
 

"""
