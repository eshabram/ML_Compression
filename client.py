import socket
from seq2seq_unigram_freq import binary_encode

def read_bin(binary_data):
    binary_data = "".join(str(bit) for bit in binary_string)
    print(f'Binary: {binary_data}')
    print(f'Binary length = {len(binary_data)}')

# get message and encode
message = input('\nEnter message:')
binary_string = binary_encode(message)
print(f'String: {binary_string}')

# Convert binary string to bytes
while len(binary_string) % 8 != 0:
    binary_string += '0'
    
binary_data = bytes(int(binary_string[i:i+8], 2) \
                    for i in range(0, len(binary_string), 8))

read_bin(binary_data)
print(f'Message length in bits: {len(message)*8}')
# Send binary data over the network
HOST = 'localhost'  # Replace with the server's IP address
PORT = 12345        # Replace with the desired port number

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(binary_data)

