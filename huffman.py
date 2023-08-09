from collections import Counter
import heapq
import argparse
import pdb

def build_huffman_tree(s):
    freq = Counter(s)
    heap = [[weight, [char, ""]] for char, weight in freq.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    
    return sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))

def huffman_encode(s):
    huffman_tree = build_huffman_tree(s)
    huff_dict = dict(huffman_tree)
    
    header = ""
    for char, code in huff_dict.items():
        header += format(ord(char), '08b') + format(len(code), '04b') + code

    encoded_message = ''.join([huff_dict[char] for char in s])
    
    return format(len(header), '016b') + header + encoded_message

def huffman_decode(encoded):
    header_length = int(encoded[:16], 2)
    header = encoded[16:16+header_length]
    message = encoded[16+header_length:]

    huff_dict = {}
    while header:
        char = chr(int(header[:8], 2))
        header = header[8:]
        
        code_len = int(header[:4], 2)
        header = header[4:]
        
        code = header[:code_len]
        header = header[code_len:]
        
        huff_dict[code] = char

    decoded = ""
    temp = ""
    for bit in message:
        temp += bit
        if temp in huff_dict:
            decoded += huff_dict[temp]
            temp = ""

    return decoded

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This script implements huffman coding.")
    parser.add_argument("-b", "--binary", \
                        action="store_true", help="Enable full printout of message binary.")
    parser.add_argument("-f", "--filepath", action="store", const=None, type=str, nargs="?")
    args = parser.parse_args()

    # read in a file or take input
    if args.filepath is not None:
        with open(args.filepath, 'r') as file:
            message = file.read()
    else:
        message = input('Enter message: ')
    
    
    encoded = huffman_encode(message)
    if len(encoded) > 100 and not args.binary:
        print(f'Encoded: ...{encoded[-100:]}')
    else:
        print(f"Encoded: {encoded}")
    orig_len = len(message) * 8
    encode_len = len(encoded)
    print(f'Original length: {orig_len}')
    print(f'Encoded length: {encode_len}')
    print(f'Percentage compression: {(encode_len / orig_len) * 100:.3g}%')
    #decoded = huffman_decode(encoded)
    #print(f"Decoded: {decoded}")
    
