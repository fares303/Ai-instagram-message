# 📱 Instagram Memory Book Generator

<p align="center">
  <img src="https://raw.githubusercontent.com/fares303/Ai-instagram-message/main/docs/images/demo.gif" alt="Instagram Memory Book Demo" width="600">
</p>

> Transform your Instagram data exports into beautiful, interactive memory books with proper text encoding and emoji support!

## ✨ Features

- 🖥️ **Modern GUI Interface** - User-friendly application with animations and dark mode
- 🔄 **Automatic Text Repair** - Fixes broken encoding in messages (especially for non-Latin scripts)
- 🎨 **Multiple Export Formats**:
  - 🌈 **HTML**: Interactive, animated conversation view
  - 📄 **PDF**: Professional document with message bubbles
  - 📝 **TXT**: Simple text format for easy reading
  - 📊 **Excel**: Detailed spreadsheet with message data
- 📊 **Conversation Statistics** - Message counts, emoji usage, activity patterns
- 📸 **Media Extraction** - Organizes photos, videos, and audio files
- 😀 **Emoji Analysis** - Counts and displays emojis used in messages
- 🔍 **Custom Word Counting** - Track specific words or emojis important to your conversations
- 🌐 **Multilingual Support** - Special handling for right-to-left languages
- 🔄 **Automatic File Detection** - Intelligently finds and processes only valid chat files

## 🚀 Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/fares303/Ai-instagram-message/main/docs/images/formats.gif" alt="Export Formats Demo" width="700">
</p>

## 📋 Requirements

- Python 3.7+
- Required packages (see `requirements.txt`)
- Instagram data export (JSON format)

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/instagram-memory-book.git
cd instagram-memory-book

# Install dependencies
pip install -r requirements.txt

# Copy and edit the configuration
cp config_sample.py config.py
```

## 🔧 Configuration

Edit `config.py` to customize your experience:

```python
# Date and time formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

# Special phrases to detect
GOOD_MORNING_PHRASES = ["good morning", "morning", "gm"]

# Add your own custom phrases to detect
CUSTOM_PHRASES = ["happy birthday", "congratulations"]
```

## 🚀 Usage

### GUI Application (Recommended)

```bash
# Run the GUI application
python run_gui.py

# On Windows, you can also double-click run_gui.bat
```

The GUI application provides a user-friendly interface with:
- Folder selection dialog
- Automatic JSON file detection
- Custom word/emoji counting
- Animated progress indicators
- Results summary view
- One-click access to output files

### Command Line Interface

```bash
# Basic usage
python run_processor.py --target_user "friend_username" --my_name "your_username" --data_path "/path/to/instagram/export" --output_path "/path/to/output"

# Or use the interactive mode
python run_processor.py --interactive
```

## 📱 Output Examples

### HTML Export
<p align="center">
  <img src="https://raw.githubusercontent.com/fares303/Ai-instagram-message/main/docs/images/html_export.png" alt="HTML Export" width="600">
</p>

### PDF Export
<p align="center">
  <img src="https://raw.githubusercontent.com/fares303/Ai-instagram-message/main/docs/images/pdf_export.png" alt="PDF Export" width="600">
</p>

## 📂 Output Structure

```
output_directory/
├── text/                  # TXT exports
├── pdf/                   # PDF exports
├── excel/                 # Excel exports
├── html/                  # HTML exports
└── media/                 # Extracted media files
    ├── photos/            # Extracted photos
    ├── videos/            # Extracted videos
    └── audio/             # Extracted audio files
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Founas Mohamed Fares**

- GitHub: [@fares303](https://github.com/fares303)
- Developer of Instagram Memory Book Generator

## 🙏 Acknowledgements

- [emoji](https://github.com/carpedm20/emoji) - For emoji processing
- [FPDF](https://github.com/reingart/pyfpdf) - For PDF generation
- [pandas](https://github.com/pandas-dev/pandas) - For data processing
- [openpyxl](https://github.com/openpyxl/openpyxl) - For Excel export
