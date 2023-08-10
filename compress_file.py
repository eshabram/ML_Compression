import argparse
import pdb
from seq2seq_unigram import *
from huffman import huffman_encode

def compress(args):
    data = 



if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="")

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
    compress(args)
    
    