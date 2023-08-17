import socket
import argparse
from seq2seq_unigram import *
from huffman import *
from utils import *

HOST = 'localhost'  # Replace with the server's IP address
PORT = 12345        # Replace with the desired port number

def run_server(args):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, PORT))
                s.listen()
                print(f'\nListening on: {HOST}:{PORT}')
                
                # receive multiple packets
                conn, addr = s.accept()
                with conn:
                    client_ip, client_port = addr
                    received_data = b''
                    while True:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        received_data += chunk
                    binary_string = ''.join(format(byte, '08b') for byte in received_data)

                    if args.verbose:
                        print("Received binary string:", binary_string)
                    if binary_string:
                        if args.lossy:
                            message = decode_sequence_lossy(binary_string, args)
                        else:
                            message = decode_sequence(binary_string, args)

                        if '\n' in message:
                            print(f'Recv From {client_ip}:\n\033[32m{message}\033[0m\nEND')
                        else:
                            print(f'Recv From {client_ip}:\n--> "\033[32m{message}\033[0m"')
                    else:
                        print("Received an empty binary string.") 
        except KeyboardInterrupt:
            print(' --Program terminated--')
            break


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-l", "--lossy", \
                        action="store_true", help="Enable advanced mode.")
    parser.add_argument("-v", "--verbose", \
                        action="store_true", help="Enable verbose mode.")
    args = parser.parse_args()
    run_server(args)
