# Instagram Data Processor

A professional Python tool to process and analyze Instagram conversation data, creating a comprehensive "Memory Book" with full statistics, decoded texts, timestamps, and media files.

## Features

- **JSON Processing**: Reads and decodes Instagram JSON message files
- **Message Formatting**: Converts timestamps and unescapes text content
- **Conversation Export**: Creates clean, readable versions of conversations in multiple formats:
  - TXT file
  - PDF file (professionally styled)
  - Excel/Google Sheets (.xlsx)
- **Statistics Generation**:
  - Total number of messages
  - Total number of emojis used
  - Number of "Good Morning" messages
  - Name mentions count
  - Active conversation days
  - Algerian slang expressions detection
- **Media Extraction**: Automatically extracts and organizes:
  - Photos
  - Videos
  - Voice messages

## Requirements

- Python 3.7+
- Required libraries:
  - pandas
  - openpyxl
  - reportlab
  - emoji
  - python-dateutil
  - Pillow
  - fpdf2
  - matplotlib

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/instagram-data-processor.git
   cd instagram-data-processor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Update the configuration in `config.py`:
   ```python
   # User configuration
   TARGET_USER = "friend_username"  # The specific user to analyze
   MY_NAME = "your_username"  # Your name for statistics

   # Path configuration
   DATA_ROOT_PATH = "path/to/instagram/data"  # Path to the Instagram data folder
   OUTPUT_PATH = "output"  # Path where output files will be saved
   ```

2. Run the main script:
   ```
   python -m instagram_data_processor.main
   ```

3. Alternatively, use command-line arguments:
   ```
   python -m instagram_data_processor.main --data-path "/path/to/data" --target-user "friend_username" --my-name "your_username"
   ```

## Output

The program creates the following output structure:
```
output/
├── text/
│   └── conversation_with_friend_username_YYYYMMDD_HHMMSS.txt
├── pdf/
│   └── conversation_with_friend_username_YYYYMMDD_HHMMSS.pdf
├── excel/
│   └── conversation_with_friend_username_YYYYMMDD_HHMMSS.xlsx
└── media/
    ├── photos/
    ├── videos/
    └── audio/
```

## Project Structure

```
instagram_data_processor/
├── __init__.py
├── main.py
├── config.py
├── json_processor.py
├── media_extractor.py
├── utils.py
├── exporters/
│   ├── __init__.py
│   ├── txt_exporter.py
│   ├── pdf_exporter.py
│   └── excel_exporter.py
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by Founas Mohamed Fares
