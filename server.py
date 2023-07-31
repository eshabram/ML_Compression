import socket
from seq2seq_unigram_freq import decode_sequence

HOST = 'localhost'  # Replace with the server's IP address
PORT = 12345        # Replace with the desired port number

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f'\nListening on: {HOST}:{PORT}')
            conn, addr = s.accept()
            with conn:
                client_ip, client_port = addr
                received_data = conn.recv(1024)
                binary_string = ''.join(format(byte, '08b') for byte in received_data)
                print("Received binary string:", binary_string)
                if binary_string:
                    result = decode_sequence(binary_string)
                    print(f'Recv From {client_ip}:\n{result}')
                else:
                    print("Received an empty binary string.") 
    except KeyboardInterrupt:
        print(' --Program terminated--')
        break