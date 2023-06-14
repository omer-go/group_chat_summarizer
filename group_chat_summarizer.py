import os
import regex as re
import openai
import datetime
from dateutil.parser import parse
import argparse
import json

DATE_PATTERN = r'(\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\])'
SUMMARY_PROMPT = f"""Please summarize the following WhatsApp group chat based on topics that were discussed. For each topic, include its title and summary in bullet points. The bullets should include detailed information. If the topic includes recommendations about specific companies or services, please include them in the summary. Please include links that were shared."""
NEWSLETTER_PROMPT = f"""Please provide one paragraph to open a newsletter covering the following topics:"""
TIME_PER_MESSAGE = 0.015  # seconds
MAX_WORD_COUNT = 2500


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    return content


def whatsapp_remove_sender(message, keep_date=False):
    start = message.find('] ')
    finish = message.find(': ')

    if keep_date:
        return message[:(start + 2)] + 'member: ' + message[(finish + 2):]
    else:
        return 'MESSAGE: ' + message[(finish + 2):]


def parse_whatsapp(text):
    message_splits = re.split(DATE_PATTERN, text)
    parsed_messages = []
    for i in range(1, len(message_splits), 2):
        message = message_splits[i] + " " + message_splits[i + 1]
        message = whatsapp_remove_sender(message)
        date_str = message_splits[i][1:-1]
        date = parse(date_str).date()
        parsed_messages.append((date, message))

    return parsed_messages


def parse_signal_chat(content):
    date_time_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]'
    messages = re.split(date_time_pattern, content)
    delimiters = re.findall(date_time_pattern, content)

    parsed_messages = []
    for i, message in enumerate(messages[1:]):
        date_time_str = delimiters[i][1:-1]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M').date()
        parsed_messages.append((date_time_obj, message.strip()))

    return parsed_messages


def signal_remove_nested_replies(text):
    pattern = r'>[^>]+>'
    while re.search(pattern, text):
        text = re.sub(pattern, '>', text)
    return re.sub(r'>', '', text)


def signal_remove_reactions_and_replies(message):
    reactions_pattern = r'\(- [\w]+: [^)]+ -\)'
    message = re.sub(reactions_pattern, '', message)
    message = signal_remove_nested_replies(message)
    message = message.replace('\n', ' ').strip()

    return message.strip()


def signal_get_messages_in_date_range(messages, start_date, end_date):
    return [msg for msg in messages if start_date <= msg[0] <= end_date]


def signal_save_messages_to_file(messages, output_directory):
    if not messages:
        print("No messages found in the specified date range.")
        return

    start_date = messages[0][0].strftime("%Y-%m-%d")
    end_date = messages[-1][0].strftime("%Y-%m-%d")
    file_name = f'{start_date}_-_{end_date}.txt'

    os.makedirs(output_directory, exist_ok=True)
    file_path = os.path.join(output_directory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        for message in messages:
            timestamp = message[0].strftime("%Y-%m-%d %H:%M")
            file.write(f"[{timestamp}] {message[1]}\n")


def signal_chunk_text(messages):
    chunks = []
    current_chunk = ""
    current_word_count = 0

    for message in messages:
        timestamp = message[0].strftime("[%Y-%m-%d %H:%M]")
        cleaned_message = timestamp + " " + signal_remove_reactions_and_replies(message[1])

        # Remove the date and replace the username with 'User'
        updated_message = re.sub(r'(?<=\])[^:]+:', 'User:', cleaned_message)
        updated_message = re.sub(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]', '', updated_message) # Comment out if you want to keep the date

        # Count the words in the message
        words = updated_message.split()
        word_count = len(words)

        if current_word_count + word_count > MAX_WORD_COUNT:
            chunks.append(current_chunk.strip())
            current_chunk = ""
            current_word_count = 0

        current_chunk += updated_message + '\n'
        current_word_count += word_count

    # Append the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def parse_slack(json_file):
    with open(json_file, 'r') as file:
        messages = json.load(file)

    parsed_messages = []
    for message in messages:
        # Ignoring system messages (join, leave, etc.)
        if 'subtype' in message:
            continue

        date = datetime.datetime.fromtimestamp(float(message['ts'])).date()
        text = message['text']
        parsed_messages.append((date, text))

    return parsed_messages


def slack_remove_sender(message):
    pattern = r'<@U[^>]+>'
    return re.sub(pattern, 'member', message)


def slack_chunk_text(messages):
    current_word_count = 0
    current_chunk = ''
    chunks = []
    for _, message in messages:
        message = slack_remove_sender(message)
        message_word_count = len(message.split())
        if current_word_count + message_word_count > MAX_WORD_COUNT:
            chunks.append(current_chunk.strip())
            current_chunk = ''
            current_word_count = 0

        current_chunk += message
        current_word_count += message_word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def filter_messages_by_dates(messages, start_day, end_day):
    filtered = []
    for message in messages:
        if message[0] < start_day:
            continue
        elif message[0] > end_day:
            break

        filtered.append(message)

    return filtered


def whatsapp_chunk_text(messages):
    current_word_count = 0
    current_chunk = ''
    chunks = []
    for _, message in messages:
        message_word_count = len(message.split())
        if current_word_count + message_word_count > MAX_WORD_COUNT:
            chunks.append(current_chunk.strip())
            current_chunk = ''
            current_word_count = 0

        current_chunk += message
        current_word_count += message_word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def call_gpt(prompt):
    model = "gpt-3.5-turbo"
    messages = [{"role": "user", "content": prompt}]
    completion = openai.ChatCompletion.create(model=model, messages=messages)
    response = completion.choices[0].message.content
    print('Response:\n' + response + '\n')

    return response


def summarize_text(text):
    prompt = f""""{SUMMARY_PROMPT}\n\n {text}"""
    return call_gpt(prompt)


def generate_newsletter_intro(text):
    prompt = f""""{NEWSLETTER_PROMPT}\n\n {text}"""
    return call_gpt(prompt)


def summarize_messages(chunks):
    summary = ''
    calls_counter = 0
    for chunk in chunks:
        calls_counter += 1
        print(f"Sending prompt {calls_counter} out of {len(chunks)} to GPT! Chunk size: {len(chunk)}")
        chunk_summary = summarize_text(chunk)
        summary += chunk_summary + '\n\n'

    return summary


def main(chat_type, chat_export_file, summary_file, start_day_s, end_day_s, is_newsletter):
    start_day = datetime.datetime.strptime(start_day_s, '%m/%d/%Y').date()
    end_day = datetime.datetime.strptime(end_day_s, '%m/%d/%Y').date()

    if chat_type == 'WhatsApp':
        content = read_file(chat_export_file)
        parsed_messages = parse_whatsapp(content)
        filtered_messages = filter_messages_by_dates(
            parsed_messages, start_day, end_day)
        chunks = whatsapp_chunk_text(filtered_messages)
    elif chat_type == 'Signal':
        content = read_file(chat_export_file)
        parsed_messages = parse_signal_chat(content)
        filtered_messages = filter_messages_by_dates(
            parsed_messages, start_day, end_day)
        chunks = signal_chunk_text(filtered_messages)
    elif chat_type == 'Slack':  # Add support for Slack
        parsed_messages = parse_slack(chat_export_file)
        filtered_messages = filter_messages_by_dates(
            parsed_messages, start_day, end_day)
        chunks = slack_chunk_text(filtered_messages)
    else:
        print('ERROR: Chat type must be either WhatsApp, Signal or Slack')
        exit(1)

    summary = summarize_messages(chunks)

    if is_newsletter:
        intro = generate_newsletter_intro(summary)
        summary = intro + '\n\n' + summary

    print(('*' * 10) + '\nSummary:\n' + ('*' * 10))
    print(summary)

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("chat_export_file",
                        help="Input file, export of the chat")
    parser.add_argument("summary_file", help="Summary output file")
    parser.add_argument("start_date", help="When to start summarizing from")
    parser.add_argument("end_date", help="Until when to summarize")
    # Update to include 'Slack'
    parser.add_argument("--chat_type", help="WhatsApp, Signal or Slack")
    parser.add_argument("--newsletter", action=argparse.BooleanOptionalAction,
                        help="Generate an introduction for a newsletter")

    args = parser.parse_args()

    # Update to include 'Slack'
    if args.chat_type not in ['WhatsApp', 'Signal', 'Slack']:
        print('ERROR: Chat type must be either WhatsApp, Signal or Slack')
        exit(1)

    if args.newsletter is not True:
        args.newsletter = False

    main(
        args.chat_type,
        args.chat_export_file,
        args.summary_file,
        args.start_date,
        args.end_date,
        args.newsletter
    )
