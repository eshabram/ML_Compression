import requests
import os
import sys
import time
import threading
import json

def loading_animation():
    cursor_anim = '|/-\\'
    i = 0
    while not animation_event.is_set():
        cursor = cursor_anim[i % len(cursor_anim)]
        with total_size_lock:
            progress_percent = int((total_size / max_data_size) * 100)
            sys.stdout.write(f"\rScraping in progress: {progress_percent}% {cursor} {(total_size / max_data_size) *100}  ")
            sys.stdout.flush()
        time.sleep(0.1)
        i += 1

def get_pushshift_data(data_type, **kwargs):
    base_url = f"https://api.pushshift.io/reddit/search/{data_type}/"
    payload = kwargs
    request = requests.get(base_url, params=payload)
    return request.json()

def fetch_comments(submission_id):
    comments_data = get_pushshift_data(data_type="comment",
                                       link_id=submission_id,
                                       size=500,
                                       sort="desc",
                                       sort_type="created_utc",
                                       fields=["body"])
    comments = [comment['body'] for comment in comments_data['data']]
    return comments

data_type="submission"
subreddit="CasualConversation"
sort_type="created_utc"
sort="desc"
fields=["selftext", "id"]
size=100

max_data_size = 1 * 1024 * 1024 * 1024
file_path = 'CasualConversation.txt'
total_size = 0
total_size_lock = threading.Lock()

# Check if the file already exists
if os.path.exists(file_path):
    print(f'{file_path} already exists. Deleting existing file...')
    os.remove(file_path)

# Start the animation thread
animation_event = threading.Event()
animation_thread = threading.Thread(target=loading_animation)
animation_thread.start()

try:
    with open(file_path, 'w') as file:
        while total_size < max_data_size:
            submissions_data = get_pushshift_data(data_type=data_type,
                                                  subreddit=subreddit,
                                                  sort_type=sort_type,
                                                  sort=sort,
                                                  size=size,
                                                  fields=fields)
            if not submissions_data['data']:
                break

            for submission in submissions_data['data']:
                conversation = submission['selftext'] + '\n'
                comments = fetch_comments(submission['id'])
                conversation += '\n'.join(comments)

                conversation_size = len(conversation.encode('utf-8'))

                # Check if adding the conversation exceeds the maximum data size
                with total_size_lock:
                    if total_size + conversation_size > max_data_size:
                        print(f'Total size: {total_size}\nConversation_size: {conversation_size}\nMax_data_size: {max_data_size}')
                        raise Exception("Max data size reached")
                    else:
                        total_size += conversation_size

                # Write the conversation to the file
                file.write(conversation + '\n')

            # set the last timestamp for the next batch
            last_timestamp = submissions_data['data'][-1]['created_utc']
            time.sleep(0.5)  # respect Pushshift's rate limit

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

print("Scraping completed.")
