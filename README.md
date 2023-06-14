# Group Chat Summarizer

This is a Python-based script that takes in the exports of your chat from either WhatsApp or Signal and provides a summarization of the conversations that occurred during a specified time period. The script uses OpenAI's GPT-4 to generate a summarized text, making it a handy tool for understanding the main points of long conversations.

This project can be used to generate summaries of your conversations or to create a paragraph that opens a newsletter covering the topics discussed during the specified time range.

## Requirements

- Python 3.7 or higher
- `openai` Python package
- `regex` Python package
- `dateutil` Python package
- `argparse` Python package
- An exported group chat from either WhatsApp or Signal

## Installation

Before installation, it's recommended to create a Python virtual environment to isolate the project dependencies. You can do this using the following commands:

```bash
python3 -m venv env
source env/bin/activate
```

Then, install the necessary Python packages by running:

```bash
pip install -r requirements.txt
```

## Exporting Chat History

To use this script, you need to have an exported group chat from either WhatsApp or Signal as a text file. Here are the instructions on how to export your chat history from each app:

### WhatsApp

To export your group chat from WhatsApp, follow these steps:

1. Open WhatsApp and go to the group chat you want to export.
2. Tap on the group name at the top of the screen to open the group info.
3. Scroll down and tap on "Export chat".
4. Choose whether to include media files or not.
5. Select how you want to share the chat export file. You can send it to yourself via email, save it to your device, or use any other method.
6. Save the chat export file as a text file with a .txt extension.

### Signal

To export your group chat from Signal, you need to use the [signal-export](https://github.com/carderne/signal-export) command-line tool. Follow these steps:

1. Install signal-export by running `pip install signal-export`.
2. Connect your Android device to your computer via USB and enable USB debugging mode.
3. Run `signal-export --output <output_directory>` in your terminal, where `<output_directory>` is the path to the folder where you want to save the chat export files.
4. Follow the instructions on your device and computer screen to grant permissions and backup your Signal data.
5. Wait for the process to finish. You should see a message saying "Done!" when it's complete.
6. Find the chat export file for the group chat you want to summarize in the output directory. It should be a text file with a .txt extension and a name that matches the group name.


### Slack
To export your Slack workspace data, follow these steps:

As an owner or admin, go to your workspace's settings by clicking on your workspace name in the top left corner, then choose "Settings & administration" -> "Workspace settings".
On the settings page, select "Import/Export Data" in the top menu, then click on "Export" -> "Start Export".
Select the data types you want to export. For this script, you need to export messages and files.
Once your download is ready, you'll receive an email with a link to download a ZIP file. Unzip this file to get a series of JSON files representing your exported data.

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

The script will print the summary to the console and write it to the output file.

## Contribution

Contributions to the project are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code follows the style of the existing project code, and add tests for any new features.

## License

See [LICENSE](./LICENSE) for more details.
