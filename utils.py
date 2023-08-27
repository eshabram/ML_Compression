import logging
import os
import PyPDF2
import re
import sys
import time



def loading_animation(animation_event, threadlocker):
    cursor_anim = '|/-\\'
    i = 0
    while not animation_event.is_set():
        cursor = cursor_anim[i % len(cursor_anim)]
        with threadlocker:
            sys.stdout.write(f"\rWorking {cursor}    ")
            sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    print('\n')


def custom_log(text_size_bits, smc_ratio, smc_huffman_ratio, huffman_ratio, gzip_ratio, zstd_ratio, level=logging.INFO):
    extra = {
        'Text_Size_Bits': text_size_bits,
        'SMC_Ratio': smc_ratio,
        'SMC_Huffman_Ratio': smc_huffman_ratio,
        'Huffman_Ratio': huffman_ratio,
        'Gzip_Ratio': gzip_ratio,
        'Zstd_Ratio': zstd_ratio
    }
    logger = logging.getLogger('SMC_logger')
    logger.log(level, '', extra=extra)


def setup_logger():
    log_file = 'data/log.csv'
    header = 'timestamp,log_level,Text Size (bits),SMC Ratio,SMC + Huffman Ratio,'\
        'Huffman Ratio,Gzip Ratio,Zstd Ratio'
    # Check if the log file exists and write the header if it's new
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write(header + '\n')

    # Define the CSV structure
    log_format = '%(asctime)s,%(levelname)s,%(Text_Size_Bits)d,%(SMC_Ratio)f,%(SMC_Huffman_Ratio)f,'\
        '%(Huffman_Ratio)f,%(Gzip_Ratio)f,%(Zstd_Ratio)f'

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



def create_pdf_from_text(text, output_path):
    pdf_writer = PyPDF2.PdfWriter()
    pdf_writer.add_page()
    
    page = pdf_writer.pages[0]
    page.merge_page(PyPDF2.pdf.PageObject.create_text_object(text))
    
    with open(output_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)


def get_filename_without_extension(file_path):
    """
    This function gets the name of the file without its path and file
    extension. This may be useful for making a file in another location, and
    linking it after the write is complete to avoid using the file before it is
    done decompressing.
    """
    base_name = os.path.basename(file_path)  
    file_name, _ = os.path.splitext(base_name)
    return file_name


def remove_non_ascii(text):
    # Remove non-ASCII characters using regular expression
    return re.sub(r'[^\x00-\x7F]+', '', text)


def file_to_binary_string(file_path):
    binary_string = ''
    with open(file_path, 'rb') as file:
        byte = file.read(1)
        while byte:
            binary_string += format(ord(byte), '08b')  # 8-bit representation of each byte
            byte = file.read(1)
    return binary_string

