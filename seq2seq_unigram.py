#%%
import pandas as pd
import numpy as np
import sys
import threading
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from huffman import *
from utils import *
import pdb

df = pd.read_csv('data/unigram_freq.csv')
# df.replace(to_replace='a', value='\n', inplace=True)

bits = [8, 16, 24, 32]
bit_code = ['00', '01', '10', '11']
threadlocker = threading.Lock()
animation_event = threading.Event()
animation_thread = threading.Thread(target=loading_animation, \
                                    args=(animation_event, threadlocker))
    
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


def binary_encode_huffman(message, args):
    # This version of encode aims to encode the max data possible, while
    # still retaining a large degree of compression.
            
    # tokenize words and punctuation (including spaces)
    tokens = nltk.regexp_tokenize(message, pattern=r' |\n|[a-zA-Z]+|\d+|[^a-zA-Z0-9\s]+')
    binary_string = ''
    huffman_ascii = ''
    header_key = ''
    no_huff = False
    group = False

    for i, token in enumerate(tokens):
        if len(token) > 1:
            key = pd.Series(word_to_key.get(token))
        else:
            key = pd.Series()
            huffman_ascii += token
        if key.empty:
            huffman_ascii += token
    if len(huffman_ascii) < 1:
        no_huff = True
    # get dictionaty translation key for tokens NOT in database
    if len(huffman_ascii) > 0:
        translation_key = build_huffman_tree(huffman_ascii, '1')
    else:
        translation_key = dict()
    
    for i, token in enumerate(tokens):
        # currently, single letters are in the dataframe, but we ignore them. 
        # To preserve capitols, change token.lower() to token, and vice versa
        if len(token) > 1:
            key = pd.Series(word_to_key.get(token))
        else:
            key = pd.Series()
        if not key.empty:
            binary_string += '1' + str(key.iloc[0])
            group = False
        else:
            # add ascii in bytes. We'll use the leading zero for decode
            if len(translation_key) > 0:
                if not group:
                    binary_string += '0' + huffman_encode_chunk(token, translation_key)
                    group = True
                else:
                    binary_string += huffman_encode_chunk(token, translation_key)

    # build header
    for char, code in translation_key.items():
        header_key += format(ord(char), '08b') + format(len(code), '04b') + code
    
    if no_huff:
        binary_string = '1' + binary_string
    else:
        header_length = len(header_key)
        header_num = format(header_length, '016b')
        pad_num = (8 - (len(binary_string) + len(header_key) + 3) % 8) % 8
        pad_str = str('{0:03b}'.format(pad_num))
        header = header_num + pad_str + header_key
        binary_string = header + binary_string
        
        # some helpful debigging print statements 
        # print(translation_key)
        # print(f'Header length: {header_length}')
        # print(f'Header 16 bit number: {header_num}')
        # print(f'Header key: {header_key}')
        # print(f'Binary: {binary_string}')
        # print(f'Padding: {pad_str}')
    
    # Convert binary string to bytes
    while len(binary_string) % 8 != 0:
        binary_string += '0'
    binary_string = bytes(int(binary_string[i:i+8], 2) \
                    for i in range(0, len(binary_string), 8))
    
    return binary_string


def binary_encode(message, args):
    # This version of encode aims to encode the max data possible, while
    # still retaining a large degree of compression.
            
    # tokenize words and punctuation (including spaces)
    tokens = nltk.regexp_tokenize(message, pattern=r' |\n|[a-zA-Z]+|\d+|[^a-zA-Z0-9\s]+')
    binary_encode = '1'
    huffman = ''
    spaces = ''
    
    # locate the index of a given word, and add it to the scheme
    for i, token in enumerate(tokens):
        # append SPACE bits
        if ' ' in token:
            for letter in token:
                # 1 to signal upcoming 2 bit code 11
                if not args.huffman:
                    binary_encode += '111'
                # huffman += letter
                # spaces += letter
            continue
        
        # currently, single letters are in the dataframe, but we ignore them. 
        # To preserve capitols, change token.lower() to token, and vice versa
        if len(token) > 1:
            key = pd.Series(word_to_key.get(token))
        else:
            key = pd.Series()
        if not key.empty:
            binary_encode += '1' + str(key.iloc[0])
        else:
            # add ascii in bytes. We'll use the leading zero for decode
            for letter in token:
                binary_encode += str(bin(ord(letter))[2:]).zfill(8)    
                huffman += letter

    
    # calls the function to convert the current message to SMC + huffman
    # if args.test:
    #     binary_encode = huffify(binary_encode)
        
    # Convert binary string to bytes
    while len(binary_encode) % 8 != 0:
        binary_encode += '0'
                
    binary_encode = bytes(int(binary_encode[i:i+8], 2) \
                    for i in range(0, len(binary_encode), 8))
    # binary_encode = caps_map + binary_encode
    return binary_encode


def decode_sequence(sequence, args):
    # this is the advanced version of the compression that aims to 
    # recreate the message as close to original as possible.
    
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 1}
    idx = 0
    message = ''
    huffman_key = dict()
    decoding_dict = dict()
    huffman = False
    
    # extract the huffman translation key
    if sequence[0] == '0':
        huffman = True
        huffman_key_len = int(sequence[:16], 2)
        pad_len = int(sequence[16:19], 2)
        print(f'Padding: {sequence[16:19]}')
        if pad_len > 0:
            sequence = sequence[:-pad_len]
        print(sequence)
        idx += 19
        while idx < huffman_key_len + 19:
            ascii_char = chr(int(sequence[idx:idx+8], 2))
            idx += 8
            code_len = int(sequence[idx:idx+4], 2)
            idx += 4
            code = sequence[idx:idx+code_len]
            decoding_dict.update({code:ascii_char})
            idx += code_len
        print(decoding_dict)
        # A reverse lookup table for huffman coded characters
        # decoding_dict = {code: char for char, code in huffman_key.items()}
        longest_key_len = max(map(len, decoding_dict.keys()))
    else:
        idx += 1
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
            # this is where we decipher the huffman codes
            if huffman: 
                idx += 1
                count = 1
                word = ''
                # since the length is not included, we incrementally grow the 
                # bit string to match the next code. This works because of the
                # unique prefixing of Huffman codes.
                while len(sequence[idx:idx+count]) <= longest_key_len and idx+count <= len(sequence):
                    if sequence[idx:idx+count] in decoding_dict:
                        word += decoding_dict[sequence[idx:idx+count]]
                        idx += count
                        count = 1
                    else:
                        count += 1
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
    

def binary_encode_lossy(message, args):
    # This function is the lossy version of the encoding scheme.
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

    while len(binary_encode) % 8 != 0:
        binary_encode += '0'
                
    binary_encode = bytes(int(binary_encode[i:i+8], 2) \
                    for i in range(0, len(binary_encode), 8))

    return binary_encode


def decode_sequence_lossy(sequence, args):
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

