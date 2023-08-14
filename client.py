import socket
import argparse
import pdb
import gzip
from seq2seq_unigram import *
from huffman import huffman_encode
import PyPDF2

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
            
            # gzip testing
            if args.gzip:
                with gzip.open('temp.gz', 'wb') as f:
                    f.write(huffman.encode('utf-8'))
                temp_size_bytes = os.path.getsize('temp.gz')
                temp_len = temp_size_bytes * 8
                huff_len = len(huffman) * 8
                msg = (bin_length - (huff_len - temp_len))
                subtract = huff_len - temp_len
                print(f'huffman length: {huff_len}')
                print(f'Temp length: {temp_len}')
                print(f'New Length: {msg}')
                print(f'With gzip: {msg / ascii_length * 100:.3g}%')
                print(f'Huff length + temp: {(len(huffman_encode(huffman)) + bin_length) / ascii_length * 100:.3g}%')
            
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
    parser.add_argument("-g", "--gzip", \
                        action="store_true", help="Use gzip compression.")
    parser.add_argument("-p", "--pdf", \
                        action="store_true", help="Read in pdf as input")
    
    args = parser.parse_args()
    run_client(args)