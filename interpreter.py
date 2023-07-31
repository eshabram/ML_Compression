def decode_sequence(sequence):
    bit_code_to_bytes = {'00': 1, '01': 2, '10': 3, '11': 4}
    idx = 0
    numbers = []

    while idx < len(sequence):
        # Extract the bit code
        bit_code = sequence[idx:idx+2]
        idx += 2

        # Determine the number of bytes to read based on the bit code
        num_bytes = bit_code_to_bytes[bit_code]

        # Read the number and convert to integer
        num_str = ''
        for _ in range(num_bytes):
            num_str += sequence[idx:idx+8]
            idx += 8
        
        numbers.append(int(num_str, 2))

    return numbers

# Test
encoded_seq = "000000110100010111110000000011010000101010100111010000111000010100"
decoded_numbers = decode_sequence(encoded_seq)
print(decoded_numbers)  # Expected: [5, 20, 333332]

print(f'Length of encoded sequence binary: {len(encoded_seq)}')