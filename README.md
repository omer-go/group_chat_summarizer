# Group Chat Summarizer

This is a Python-based script that takes in the exports of your chat from either WhatsApp or Signal and provides a summarization of the conversations that occurred during a specified time period. The script uses OpenAI's GPT-4 to generate a summarized text, making it a handy tool for understanding the main points of long conversations.

This project can be used to generate summaries of your conversations or to create a paragraph that opens a newsletter covering the topics discussed during the specified time range.

## Requirements

- Python 3.7 or higher
- `openai` Python package
- `regex` Python package
- `dateutil` Python package
- `argparse` Python package

## Installation

To install the requirements, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Usage

To use this script, navigate to the directory containing the script, and run it in the terminal. The basic usage is:

```bash
python main.py <chat_export_file> <summary_file> <start_date> <end_date> --chat_type=<chat_type> --newsletter=<boolean>
```

Here's a description of the command-line arguments:

- `chat_export_file`: This is the path to the text file that contains your chat history export.
- `summary_file`: This is the path to the output text file where the summary will be written.
- `start_date`: This is the date from which the summary should start. The format should be "mm/dd/yyyy".
- `end_date`: This is the date till which the summary should go. The format should be "mm/dd/yyyy".
- `--chat_type`: This optional argument specifies the type of chat export. The valid inputs are 'WhatsApp' or 'Signal'.
- `--newsletter`: This optional boolean argument, when set to `True`, instructs the script to generate an introduction for a newsletter.

For example:

```bash
python main.py chat_export.txt summary.txt 01/01/2023 01/31/2023 --chat_type=WhatsApp --newsletter=True
```

## Contribution

Contributions to the project are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code follows the style of the existing project code, and add tests for any new features.

## License

See [LICENSE](./LICENSE) for more details.
