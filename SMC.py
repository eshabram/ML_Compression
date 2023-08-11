import argparse
import pdb
from seq2seq_unigram import binary_encode, decode_sequence
from huffman import huffman_encode
import os

def get_filename_without_extension(file_path):
    """
    This function is gets the name of the file without its path and file
    extension. This may be useful for making a file in another location, and
    lining it after the write is complete to avoid using the file before it is
    done decompressing.
    """
    base_name = os.path.basename(file_path)  
    file_name, _ = os.path.splitext(base_name)
    return file_name


def compress(args):
    file_name = get_filename_without_extension(args.filepath)
    
    with open(args.filepath, 'r') as file:
        file_content = file.read()
        encoded_data, nothing, morenothing = binary_encode(file_content, args)

    # Construct the new filename with a '.smc' extension
    file_directory, file_name_with_extension = os.path.split(args.filepath)
    file_name, _ = os.path.splitext(file_name_with_extension)
    new_file_path = os.path.join(file_directory, file_name + '.smc')
    
    # Write the encoded data to the new file
    with open(new_file_path, 'wb') as new_file:
        new_file.write(encoded_data)
        
def decompress(args):
    if args.filepath[-3:] != 'smc' and not args.force:
        print('Incorrect filetype. Please use .smc filetype.')
        exit()
    # read binary file
    with open(args.filepath, 'rb') as file:
        file_data = file.read()
        file_content = ''.join(format(byte, '08b') for byte in file_data)
        decoded_data = decode_sequence(file_content, args)

        
        # Construct the new filename with a '.smc' extension
        file_directory, file_name_with_extension = os.path.split(args.filepath)
        file_name, _ = os.path.splitext(file_name_with_extension)
        new_file_path = os.path.join(file_directory, file_name + '.uncompressed')

        # Write the encoded data to the new file
        with open(new_file_path, 'w') as new_file:
            new_file.write(decoded_data)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="")
    
    parser.add_argument("filepath", type=str, help="File path to be compressed.")
    parser.add_argument("-v", "--verbose", \
                        action="store_true", help="Enable verbose mode.")
    parser.add_argument("--huffman", \
                        action="store_true", help="Measure message against Huffman coding.")
    parser.add_argument("-s", "--supercompress", \
                        action="store_true", help="Enable supercompress.")
    parser.add_argument("-d", "--decompress", \
                        action="store_true", help="Decompress SMC file.")
    parser.add_argument("-f", "--force", \
                        action="store_true", help="Enable test mode.")
    parser.add_argument("-t", "--test", \
                        action="store_true", help="Enable test mode.")
    
    args = parser.parse_args()
    if args.decompress:
        decompress(args)
    else:
        compress(args)
    
    