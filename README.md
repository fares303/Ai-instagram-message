# 📱 Instagram Memory Book Generator

<p align="center">
  <img src="https://i.imgur.com/XYZ123.gif" alt="Instagram Memory Book Demo" width="600">
</p>

> Transform your Instagram data exports into beautiful, interactive memory books with proper text encoding and emoji support!

## ✨ Features

- 🔄 **Automatic Text Repair** - Fixes broken encoding in messages (especially for non-Latin scripts)
- 🎨 **Multiple Export Formats**:
  - 🌈 **HTML**: Interactive, animated conversation view
  - 📄 **PDF**: Professional document with message bubbles
  - 📝 **TXT**: Simple text format for easy reading
  - 📊 **Excel**: Detailed spreadsheet with message data
- 📊 **Conversation Statistics** - Message counts, emoji usage, activity patterns
- 📸 **Media Extraction** - Organizes photos, videos, and audio files
- 😀 **Emoji Analysis** - Counts and displays emojis used in messages
- 🌐 **Multilingual Support** - Special handling for right-to-left languages

## 🚀 Demo

<p align="center">
  <img src="https://i.imgur.com/XYZ456.gif" alt="Export Formats Demo" width="700">
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

```bash
# Basic usage
python run_processor.py --target_user "friend_username" --my_name "your_username" --data_path "/path/to/instagram/export" --output_path "/path/to/output"

# Or use the interactive mode
python run_processor.py --interactive
```

## 📱 Output Examples

### HTML Export
<p align="center">
  <img src="https://i.imgur.com/XYZ789.png" alt="HTML Export" width="600">
</p>

### PDF Export
<p align="center">
  <img src="https://i.imgur.com/ABC123.png" alt="PDF Export" width="600">
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

## 🙏 Acknowledgements

- [emoji](https://github.com/carpedm20/emoji) - For emoji processing
- [FPDF](https://github.com/reingart/pyfpdf) - For PDF generation
- [pandas](https://github.com/pandas-dev/pandas) - For data processing
- [openpyxl](https://github.com/openpyxl/openpyxl) - For Excel export
