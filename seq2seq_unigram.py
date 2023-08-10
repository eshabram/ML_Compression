#%%
import pandas as pd
import numpy as np
import os
import sys
import time
import threading
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from huffman import *
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


def binary_encode_advanced(message, args):
    # This version of encode aims to encode the max data possible, while
    # still retaining a large degree of compression.
    
    # build a map for capitol letters
    # caps_map = ''
    # for letter in message:
    #     if letter.islower():
    #         caps_map += '0'
    #     elif letter.isupper():
    #         caps_map += '1'
            
    # tokenize words and punctuation (including spaces)
    tokens = nltk.regexp_tokenize(message, pattern=r' |\n|[a-zA-Z]+|\d+|[^a-zA-Z0-9\s]+')
  
    binary_encode = ''
    huffman = ''
    spaces = ''
    
    # locate the index of a given word, and add it to the scheme
    for i, token in enumerate(tokens):
        # append SPACE bits
        if ' ' in token:
            for letter in token:
                # 1 to signal upcoming 2 bit code 11
                binary_encode += '111'
                huffman += letter
                spaces += letter
            continue
        # currently, single letters are in the dataframe, but we ignore them. 
        # To preserve capitols, change token.lower() to token, and vice versa
        if len(token) > 1:
            key = df.loc[df['word'] == token, 'key']
        else:
            key = pd.Series()
        if not key.empty:
            binary_encode += '1' + str(key.iloc[0])
        else:
            # add ascii in bytes. We'll use the leading zero for decode
            for letter in token:
                binary_encode += str(bin(ord(letter))[2:]).zfill(8)    
                huffman += letter

    """
    This part calls the function to convert the current message to SMC + huffman
    
    """
    if args.test:
        binary_encode = huffify(binary_encode)
    # add capitols map
    # binary_encode = caps_map + binary_encode
    return binary_encode, huffman, spaces


def decode_sequence_advanced(sequence, args):
    # this is the advanced version of the compression that aims to 
    # recreate the message as close to original as possible.
    
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 1}
    idx = 0
    message = ''
    # get the capitols map if there is one
#    if sequence[0] == 1:
#        caps_map = sequence[1:]
        
    while idx < len(sequence) and len(sequence) - idx >= 8:
        num_str = ''
        if sequence[idx] == '1':
            idx += 1
            # Extract the bit code
            bit_code = sequence[idx:idx+2]
            idx += 2
            
            if bit_code == '11':
                # deal with spacing
                message += ' '
                continue

            # Determine the number of bytes to read based on the bit code
            num_bytes = bit_code_to_bytes[bit_code]
    
            # Read the number and convert to integer
            for _ in range(num_bytes):
                if len(sequence) - idx < 8:
                    break
                num_str += sequence[idx:idx+8]
                idx += 8
                
            if num_str:
                index_value = int(num_str, 2)
                    
            message += get_word(index_value)

        else:
            word = ''
            if len(message) != 0:
                message + ' '
            try:
                while sequence[idx] == '0':
                    # Convert the 8-bit code to an integer
                    ascii_code = int(sequence[idx:idx+8], 2)  
                    # Convert the integer to the corresponding ASCII character
                    ascii_character = chr(ascii_code)  
                    word += ascii_character      
                    idx += 8
            except IndexError:
                pass
            
            message  += word
    return message

def huffify(sequence):
    """ 
    TODO: 
    I need to make this function convert the ascii portion of "sequence"
    to the huffman codes. To do this, I will need to call huffman_encode(sequence, prefix=0)
    in order to get the translation key. The translation key should likely be
    appended to the beginning of the message so that it can be read in and saved
    by the decoder. I will also add a bit the the beginning after I've updated 
    and returned this sequence in the encode function. This will indicate to the 
    server that is should be decoded in one of two ways. 
    """
    
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 1}
    idx = 0
    message = ''
        
    while idx < len(sequence) and len(sequence) - idx >= 8:
        num_str = ''
        if sequence[idx] == '1':
            idx += 1
            # Extract the bit code
            bit_code = sequence[idx:idx+2]
            idx += 2
            
            if bit_code == '11':
                # deal with spacing
                message += ' '
                continue

            # Determine the number of bytes to read based on the bit code
            num_bytes = bit_code_to_bytes[bit_code]
    
            # Read the number and convert to integer
            for _ in range(num_bytes):
                if len(sequence) - idx < 8:
                    break
                num_str += sequence[idx:idx+8]
                idx += 8
                
            if num_str:
                index_value = int(num_str, 2)
                    
            message += get_word(index_value)

        else:
            word = ''
            if len(message) != 0:
                message + ' '
            try:
                while sequence[idx] == '0':
                    # Convert the 8-bit code to an integer
                    ascii_code = int(sequence[idx:idx+8], 2)  
                    # Convert the integer to the corresponding ASCII character
                    ascii_character = chr(ascii_code)  
                    word += ascii_character      
                    idx += 8
            except IndexError:
                pass
            
            message  += word
    return message
    

def binary_encode(message, args):
    # This function is the simple/light-weight version of the encoding scheme.
    # this version retains as much meaning as possible while keeping the 
    # compression down between 30% and 40%. It doesn't handle numbers well.
    
    # tokenize words and punctuation
    tokens = nltk.word_tokenize(message)
    if args.verbose:
        print(tokens)
    # Filter out punctuation
    #tokens = [token for token in tokens if token not in string.punctuation]
    
    binary_encode = ''
    
    # locate the index of a given word, and add it to the scheme
    for token in tokens:    
        if len(token) > 1:
            key = df.loc[df['word'] == token.lower(), 'key']
        else:
            key = pd.Series()
        if not key.empty:
            binary_encode += '1' + str(key.iloc[0])
        else:
            for letter in token:
                binary_encode += str(bin(ord(letter))[2:]).zfill(8)                
            if args.verbose:
                print(f"Warning: Token '{token}' not found in dataframe. Sending as ascii representation.")


    return binary_encode


def decode_sequence(sequence, args):
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

    

# assign key values with custom scheme, based on the index of a word.
# Index = rank. Keys are shorter for more common words.
animation_thread.start()
df['key'] = df.index.map(lambda x: encode_number(x, bits, bit_code))
word_to_key = dict(zip(df['word'], df['key']))


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
-----------------------------------------------
Description of Advanced Mode:
    
First bit indicates an index value. If the index bit is set to 1, then the next
two bits are read and interpreted, where 00 idicates only one byte to be read, 
01 indicates two, 10 indicates three, and 11 incidates a space. If the first bit
is a 0, then the next 7 bits is encoded as the ascii character representation. 
In this way, the message can be, at largest, 100% the size of the original 
message. This is currently how capitol letters are dealt with, but may change 
in the future (perhaps to a capitols map).


NOTE: I could add a bit after 1 11 for a space to always be read and have it 
represent either a space or a newline. Then the question would be, how many 
spaces per line? If it were 8 spaces per newline character on average, then the
newline char might benefit from the added functionality, but otherwise it would
make the message bigger. We may be better off going with adding the "\n" to the 
dictionary.   

IDEA: Since the advanced encoding deals more with text of all kinds, including 
newlines and things such as python code, then it would be a good idea to integrate
Huffman encoding for the ascii character after a certain point. I say after a 
certain point because small messages like "How are you?" have a negative benefit 
from Huffman encoding due to lack of duplicate characters and the inclusion of
the translation key. 

1300 is the length of the worst case scenario for when huffman begins to have
a positive impact. 
-----------------------------------------------
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

def binary_encode_advanced(message, args):
    # This version of encode aims to encode the max data possible, while
    # still retaining a large degree of compression.
            
    # tokenize words and punctuation (including spaces)
    tokens = nltk.regexp_tokenize(message, pattern=r' |\n|[a-zA-Z]+|\d+|[^a-zA-Z0-9\s]+')
  
    binary_encode = ''
    huffman = ''
    spaces = ''
    key = pd.Series()
    
    # locate the index of a given word, and add it to the scheme
    for i, token in enumerate(tokens):
        # append SPACE bits
        if ' ' in token:
            for letter in token:
                # 1 to signal upcoming 2 bit code 11
                binary_encode += '111'
                huffman += letter
                spaces += letter
            continue
        # currently, single letters are in the dataframe, but we ignore them. 
        # To preserve capitols, change token.lower() to token, and vice versa
        if len(token) > 1:
            key = word_to_key.get(token, pd.Series())
        if isinstance(key, pd.Series) and not key.empty:
            binary_encode += '1' + str(key.iloc[0])
        else:
            # add ascii in bytes. We'll use the leading zero for decode
            for letter in token:
                binary_encode += str(bin(ord(letter))[2:]).zfill(8)    
                huffman += letter

    if args.test:
        binary_encode = huffify(binary_encode)
    # add capitols map
    # binary_encode = caps_map + binary_encode
    return binary_encode, huffman, spaces

"""
