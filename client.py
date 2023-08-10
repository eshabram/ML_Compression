import socket
import argparse
import pdb
from seq2seq_unigram import *
from huffman import huffman_encode

def run_client(args):
    print('\n')
    while True:
        try:
            def read_bin(binary_data):
                pad = 0
                binary_data = "".join(str(bit) for bit in binary_string)
                if len(binary_data) % 8 != 0:
                    pad = 8 - len(binary_data)
                if args.verbose:
                    if len(binary_data) > 100:
                        print(f'Binary data: ...{binary_data[-100:]}')
                    else:
                        print(f'Binary data: {binary_data}')
                print(f'Binary length = {len(binary_data)} + {pad} padding')
                return len(binary_data) + pad
            
            if args.filepath is not None:
                with open(args.filepath, 'r') as file:
                    message = file.read()
            else:
                # get message and encode
                message = input('Enter message: ')
            if len(message) == 0:
                continue
            if args.lossy:
                binary_string = binary_encode_lossy(message, args)
            else:
                binary_string, huffman, spaces = binary_encode(message, args)
            if args.verbose:
                bin_data = ''.join(format(byte, '08b') for byte in binary_string)
                if len(binary_string) > 100:
                    print(f'Binary string: ...{bin_data[-100:]}')
                else:
                    print(f'Binary string: {bin_data}')
            
            
            bin_length = len(binary_string) * 8
            print(f'Bin_length: {bin_length}')
            ascii_length = len(message) * 8


            print(f'Message before compression: {ascii_length} bits')
            print(f'% of original - SMC: {bin_length / ascii_length * 100:.3g}%')
            if args.supercompress and len(huffman) != 0:
                huff_encode = huffman_encode(huffman)                
                huffman_len = len(huffman) * 8
                encoded_len = len(huff_encode)
                # subtract 5 bits for every space to compensate for 111 code
                after_space_encode = (huffman_len - (len(spaces) * 5))
                improvement = encoded_len / after_space_encode
                print('---------------------------Huffman----------------------------')
                print(f'ASCII bits length: {huffman_len}')
                print(f'ASCII after spc encode: {after_space_encode}')
                print(f'huff bits length: {encoded_len}')
                print(f'Potential Improvement: {100 - improvement * 100:.3g}%')
                perc_both = (bin_length - (after_space_encode - encoded_len)) / ascii_length * 100
                print(f'SMC + Huffman potentially: {perc_both:.3g}% of original size.')
            
            # get huffman coded length of message
            if args.huffman:
                huff_len = len(huffman_encode(message))
                print(f'% of original - Huf: {(huff_len / ascii_length) * 100:.3g}%')
            print('\n')
            
            # Send binary data over the network
            HOST = 'localhost'  # Replace with the server's IP address
            PORT = 12345        # Replace with the desired port number
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(binary_string)
            s.close()
            if args.filepath is not None:
                break
        except KeyboardInterrupt:
            print(' --Program terminated.--')
            break


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-l", "--lossy", \
                        action="store_true", help="Enable lossy mode.")
    parser.add_argument("-v", "--verbose", \
                        action="store_true", help="Enable verbose mode.")
    parser.add_argument("--huffman", \
                        action="store_true", help="Measure message against Huffman coding.")
    parser.add_argument("-f", "--filepath", action="store", const=None, type=str, nargs="?")
    parser.add_argument("-s", "--supercompress", \
                        action="store_true", help="Enable advanced mode.")
    parser.add_argument("-t", "--test", \
                        action="store_true", help="Enable advanced mode.")
    
    args = parser.parse_args()
    run_client(args)