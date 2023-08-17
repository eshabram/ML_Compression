import socket
import argparse
import pdb
import gzip
import os
from seq2seq_unigram import *
from huffman import huffman_encode
from utils import *
import logging


def run_client(args):
    print('\n')
    while True:
        try:
            if args.filepath is not None:
                if args.pdf:
                    message = extract_text_from_pdf(args.filepath)
                else:
                    with open(args.filepath, 'r') as file:
                        message = file.read()
            else:
                # get message and encode
                message = input('Enter message: ')
            if len(message) == 0:
                continue
            if args.lossy:
                binary_string = binary_encode_lossy(message, args)
            elif args.huffman:
                binary_string = binary_encode_huffman(message, args)
            else:
                binary_string = binary_encode(message, args)
            
            # test mode runs all encodes and logs the data, and sends SMC_only
            if args.test:
                SMC_huffman = binary_encode_huffman(message, args)
                huffman_only = huffman_encode(message)
                with gzip.open('temp.gz', 'wb') as f:
                    f.write(message.encode('utf-8'))
                temp_size_bytes = os.path.getsize('temp.gz')
                temp_len = temp_size_bytes * 8
                os.remove('temp.gz')
            bin_data = ''.join(format(byte, '08b') for byte in binary_string)
    
            if args.verbose:
                if len(binary_string) > 100:
                    print(f'Binary string: ...{bin_data[-100:]}')
                else:
                    print(f'Binary string: {bin_data}')
            
            
            SMC_length = len(bin_data)
            orig_length = len(message) * 8
            SMC_perc = (orig_length - SMC_length) / orig_length
            print(f'SMC length: {SMC_length}')
            print(f'Message before compression: {orig_length} bits')
            print(f'Compression Ratio - SMC: {SMC_perc * 100:.3g}%')

            if args.test:
                SMC_huff_len = len(SMC_huffman) * 8
                huff_len = len(huffman_only) 
                SMC_huff_perc = (orig_length - SMC_huff_len) / orig_length
                huff_perc = (orig_length - huff_len) / orig_length
                gzip_perc = (orig_length - temp_len) / orig_length
                print(f'Compression Ratio - S+H: {SMC_huff_perc * 100:.3g}%')
                print(f'Compression Ratio - huf: {huff_perc * 100:.3g}%')
                print(f'Compression Ratio -  gz: {gzip_perc * 100:.3g}%')
                custom_log(orig_length, SMC_perc, SMC_huff_perc, huff_perc, gzip_perc)

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

    parser.add_argument("-t", "--test", \
                        action="store_true", help="Enable test mode.")
    parser.add_argument("-p", "--pdf", \
                        action="store_true", help="Read in pdf as input")
        
    setup_logger()
    
    args = parser.parse_args()
    run_client(args)
