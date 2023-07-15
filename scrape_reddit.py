import praw
import os
import sys
import time
import threading

def loading_animation():
    cursor_anim = '|/-\\'
    i = 0
    while not animation_event.is_set():
        cursor = cursor_anim[i % len(cursor_anim)]
        with total_size_lock:
            sys.stdout.write(f"\rScraping in progress: {((total_size / max_data_size) *100):.2g}% {cursor}   ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1


reddit = praw.Reddit(client_id='uHEfoWv1Jp1dCT3Ff2gF4A', \
                               client_secret='hD6U0U74B9iuSpFbp_dNqHFVhXVFhQ', \
                                user_agent='ML_compression_v1', check_for_async=False)

total_size = 0
count = 0
file_path = 'reddit_data.txt'
max_data_size = 1 * 1024 * 1024 * 1024
total_size_lock = threading.Lock()
pop_list = []

# Check if the file already exists
if os.path.exists(file_path):
    print(f'{file_path} already exists. Deleting existing file...')
    os.remove(file_path)

# find top 20 subreddits
pop = reddit.subreddits.popular(limit=10000)
for sub in pop:
    pop_list.append(sub.display_name)
    

while True:
    if count >= len(pop_list):
        print("We're gunna need a bigger list...")
        break
    subreddit = reddit.subreddit(pop_list[count])

    # Start the animation thread
    animation_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation)
    animation_thread.start()
    
    try:
    # Read text from file
        with open(file_path, 'a') as file:
            # Scrape conversations
            for submission in subreddit.new(limit=None):
                conversation = submission.title + ' ' + submission.selftext
                conversation_size = len(conversation.encode('utf-8'))
    
                # Check if adding the conversation exceeds the maximum data size
                with total_size_lock:
                    if total_size + conversation_size > max_data_size:
                        break
                    else:
                        total_size += conversation_size
        
                # Write the conversation to the file
                file.write(conversation + '\n')
    
    
    except KeyboardInterrupt:
        # Keyboard interrupt received, stop the animation and join the animation thread
        animation_event.set()
        animation_thread.join()
        print("\nProgram halted by user.")
        sys.exit(0)
        
    finally:
        #join animation thread
        animation_event.set()
        animation_thread.join()
        count += 1

        # if total_size + conversation_data < max_data_size:
        #     continue
        # else:
        #     break
    

print("Scraping completed.")