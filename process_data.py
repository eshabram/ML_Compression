import argparse
import gzip
from huffman import huffman_encode
from seq2seq_unigram import binary_encode, binary_encode_huffman
from utils import *
import threading
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def run_tests(args):
    with open('data/human_chat.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        message = remove_non_ascii(line)[9:]
        binary_string = binary_encode(message, args)
        SMC_huffman = binary_encode_huffman(message, args)
        huffman_only = huffman_encode(message)
        with gzip.open('temp.gz', 'wb') as f:
            f.write(message.encode('utf-8'))
        temp_size_bytes = os.path.getsize('temp.gz')
        temp_len = temp_size_bytes * 8
        os.remove('temp.gz')
        bin_data = ''.join(format(byte, '08b') for byte in binary_string) 
        SMC_length = len(bin_data)
        orig_length = len(message) * 8
        SMC_perc = (orig_length - SMC_length) / orig_length
        SMC_huff_len = len(SMC_huffman) * 8
        huff_len = len(huffman_only) 
        SMC_huff_perc = (orig_length - SMC_huff_len) / orig_length
        huff_perc = (orig_length - huff_len) / orig_length
        gzip_perc = (orig_length - temp_len) / orig_length
        custom_log(orig_length, SMC_perc, SMC_huff_perc, huff_perc, gzip_perc)
        
def run_plot(args):
    df = pd.read_csv('data/log.csv')
    df.columns    

    # Subset the DataFrame and filter text sizes within a specific range
    df_plot = df[(df['Text Size (bits)'] >= 0) & (df['Text Size (bits)'] <= 2240)]
    df_plot = df_plot[['Text Size (bits)', 'SMC Ratio','SMC + Huffman Ratio', 'Huffman Ratio', 'Gzip Ratio']]    
    df_plot['Text Size (bits)'].max()
    # Calculate mean ratios for each column
    mean_ratios = df_plot.groupby('Text Size (bits)').mean()
    # Reset index to make 'Text Size (bits)' a regular column
    mean_ratios = mean_ratios.reset_index()
    
    # Set the style using Seaborn
    sns.set(style="whitegrid")
    
    # Create the line plot using Seaborn
    plt.figure(figsize=(12, 6))  # Set the figure size
    sns.lineplot(data=mean_ratios, x='Text Size (bits)', y='SMC Ratio', label='SMC Ratio')
    sns.lineplot(data=mean_ratios, x='Text Size (bits)', y='SMC + Huffman Ratio', label='SMC + Huffman Ratio')
    sns.lineplot(data=mean_ratios, x='Text Size (bits)', y='Huffman Ratio', label='Huffman Ratio')
    sns.lineplot(data=mean_ratios, x='Text Size (bits)', y='Gzip Ratio', label='Gzip Ratio')
    
    # Set title and labels
    plt.title('Comparison of Compression Ratios by Text Size')
    plt.xlabel('Text Size (bits)')
    plt.ylabel('Mean Ratios')
    plt.ylim(-1, 1)  # Adjust these limits based on your data range
    plt.axhline(y=0, color='gray', linestyle='dashed')
    
    # Get the minimum and maximum text size values for x-axis limits
    min_text_size = df_plot['Text Size (bits)'].min()
    max_text_size = df_plot['Text Size (bits)'].max()
    
    # Set x-axis limits to match the edge of the data
    plt.xlim(min_text_size, max_text_size)
    # Display legend
    plt.legend(loc='lower right')
    
    # Show the plot
    plt.show()

        
        
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--test", \
                        action="store_true", help="Run tests.")
    parser.add_argument("--huffman", \
                        action="store_true", help="Measure message against Huffman coding.")
    args = parser.parse_args()
    
    threadlocker = threading.Lock()
    animation_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation, \
                                        args=(animation_event, threadlocker))
        
    setup_logger()

    
    if args.test:
        animation_thread.start()
        run_tests(args)
        animation_event.set()
        animation_thread.join()
    else: 
        run_plot(args)