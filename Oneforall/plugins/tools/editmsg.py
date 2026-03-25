import time

# Function to check for changes in message content
def should_delete_message(old_content, new_content):
    return old_content != new_content

# Auto-delete message after 5 seconds
if __name__ == '__main__':
    old_message = "Original message"
    new_message = "New message"
    
    if should_delete_message(old_message, new_message):
        time.sleep(5)
        print('Message deleted after 5 seconds.')
    else:
        print('Message not deleted since the content did not change.')
