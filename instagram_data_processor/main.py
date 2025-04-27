"""
Main module for Instagram Data Processor.

This script processes Instagram data downloaded from Instagram and creates
a "Memory Book" with conversation analysis, statistics, and media files.

Usage:
    python main.py

Author: Fares
"""

import os
import sys
import logging
import argparse
from datetime import datetime

import instagram_data_processor.config as config
from instagram_data_processor.json_processor import InstagramDataProcessor
from instagram_data_processor.media_extractor import MediaExtractor
from instagram_data_processor.exporters import TxtExporter, PDFExporter, ExcelExporter
import instagram_data_processor.utils as utils

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Process Instagram data and create a Memory Book.')

    parser.add_argument('--data-path', type=str, default=config.DATA_ROOT_PATH,
                        help='Path to Instagram data folder')

    parser.add_argument('--output-path', type=str, default=config.OUTPUT_PATH,
                        help='Path to output folder')

    parser.add_argument('--target-user', type=str, default=config.TARGET_USER,
                        help='Name of the target user to analyze')

    parser.add_argument('--my-name', type=str, default=config.MY_NAME,
                        help='Your name')

    return parser.parse_args()

def main():
    """
    Main function to process Instagram data.
    """
    # Parse command line arguments
    args = parse_arguments()

    # Print welcome message
    print("\n" + "=" * 80)
    print(f"Instagram Data Processor - Memory Book Generator")
    print("=" * 80)
    print(f"Target User: {args.target_user}")
    print(f"Data Path: {args.data_path}")
    print(f"Output Path: {args.output_path}")
    print("=" * 80 + "\n")

    # Validate paths
    if not os.path.exists(args.data_path):
        logger.error(f"Data path does not exist: {args.data_path}")
        print(f"Error: Data path does not exist: {args.data_path}")
        return 1

    # Create output directories
    output_dirs = utils.setup_directories(args.output_path)

    try:
        # Step 1: Process JSON files
        print("Step 1: Processing JSON files...")
        processor = InstagramDataProcessor(args.data_path, args.target_user, args.my_name)
        messages = processor.process_json_files()

        if not messages:
            logger.error(f"No messages found for user: {args.target_user}")
            print(f"Error: No messages found for user: {args.target_user}")
            return 1

        print(f"Found {len(messages)} messages for {args.target_user}")

        # Step 2: Generate statistics
        print("\nStep 2: Generating statistics...")
        stats = processor.get_conversation_stats()

        print(f"Total messages: {stats['total_messages']}")
        print(f"Messages from {args.my_name}: {stats['messages_by_sender'].get(args.my_name, 0)}")
        print(f"Messages from {args.target_user}: {stats['messages_by_sender'].get(args.target_user, 0)}")
        print(f"Total emojis: {stats['total_emojis']}")
        print(f"Good morning messages: {stats['good_morning_count']}")
        print(f"Conversation duration: {stats['conversation_duration_days']} days")

        # Step 3: Extract media files
        print("\nStep 3: Extracting media files...")
        media_extractor = MediaExtractor(args.data_path, args.output_path, args.target_user)
        media_stats = media_extractor.extract_all_media(messages)

        print(f"Extracted {media_stats['photos']} photos")
        print(f"Extracted {media_stats['videos']} videos")
        print(f"Extracted {media_stats['audio']} audio files")

        # Step 4: Export to different formats
        print("\nStep 4: Exporting conversation...")

        # Export to TXT
        print("Exporting to TXT...")
        txt_exporter = TxtExporter(output_dirs["text"])
        txt_file = txt_exporter.export(messages, args.target_user, args.my_name, stats)

        # Export to PDF
        print("Exporting to PDF...")
        pdf_exporter = PDFExporter(output_dirs["pdf"])
        pdf_file = pdf_exporter.export(messages, args.target_user, args.my_name, stats)

        # Export to Excel
        print("Exporting to Excel...")
        excel_exporter = ExcelExporter(output_dirs["excel"])
        excel_file = excel_exporter.export(messages, args.target_user, args.my_name, stats)

        # Print summary
        print("\n" + "=" * 80)
        print("Memory Book Generation Complete!")
        print("=" * 80)
        print(f"Output files:")
        if txt_file:
            print(f"- TXT: {os.path.basename(txt_file)}")
        if pdf_file:
            print(f"- PDF: {os.path.basename(pdf_file)}")
        if excel_file:
            print(f"- Excel: {os.path.basename(excel_file)}")
        print(f"- Media files: {media_stats['total']} files extracted")
        print("\nOutput directory: {0}".format(os.path.abspath(args.output_path)))
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error processing Instagram data: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
