import socket
import argparse
import pdb
import gzip
import os
from seq2seq_unigram import *
from huffman import huffman_encode
import PyPDF2
import logging

def custom_log(text_size_bits, smc_improvement, smc_huffman_improvement, huffman_improvement, gzip_improvement, level=logging.INFO):
    extra = {
        'Text_Size_Bits': text_size_bits,
        'SMC_improvement': smc_improvement,
        'SMC_Huffman_Improvement': smc_huffman_improvement,
        'Huffman_Improvement': huffman_improvement,
        'Gzip_Improvement': gzip_improvement
    }
    logger = logging.getLogger('SMC_logger')
    logger.log(level, '', extra=extra)


def setup_logger():
    log_file = 'data/log.csv'
    header = 'timestamp,log_level,Text Size (bits),SMC Improvement,SMC Huffman Improvment,'\
        'Huffman Improvement,Gzip Improvement'
    # Check if the log file exists and write the header if it's new
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write(header + '\n')

    # Define the CSV structure
    log_format = '%(asctime)s,%(levelname)s,%(Text_Size_Bits)d,%(SMC_improvement)f,%(SMC_Huffman_Improvement)f,'\
        '%(Huffman_Improvement)f,%(Gzip_Improvement)f'

    # Setup the logger
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,  # Set the minimum log level
        format=log_format,
        filemode='a'  # Set the file mode (append mode)
    )
    logger = logging.getLogger('SMC_logger')
    
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

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
            ascii_length = len(message) * 8
            print(f'SMC length: {SMC_length}')
            print(f'Message before compression: {ascii_length} bits')
            print(f'% of original - SMC: {SMC_length / ascii_length * 100:.3g}%')

            if args.test:
                SMC_huff_len = len(SMC_huffman) * 8
                huff_len = len(huffman_only) 
                print(f'% of original - S+H: {SMC_huff_len / ascii_length * 100:.3g}%')
                print(f'% of original - huf: {huff_len / ascii_length * 100:.3g}%')
                print(f'% of original -  gz: {temp_len / ascii_length * 100:.3g}%')

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