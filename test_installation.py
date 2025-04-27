#!/usr/bin/env python
"""
Test script to verify the Instagram Data Processor installation.

This script checks if all required dependencies are installed and
the project structure is correct.
"""

import sys
import importlib
import os

def check_dependency(module_name):
    """Check if a Python module is installed."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to test the installation."""
    print("Testing Instagram Data Processor installation...\n")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required")
        return False
    
    # Check required dependencies
    dependencies = [
        "pandas",
        "openpyxl",
        "reportlab",
        "emoji",
        "dateutil",
        "PIL",
        "fpdf",
        "matplotlib"
    ]
    
    all_deps_installed = True
    print("\nChecking dependencies:")
    for dep in dependencies:
        installed = check_dependency(dep)
        status = "OK" if installed else "MISSING"
        print(f"  {dep}: {status}")
        if not installed:
            all_deps_installed = False
    
    # Check project structure
    print("\nChecking project structure:")
    required_files = [
        "instagram_data_processor/__init__.py",
        "instagram_data_processor/main.py",
        "instagram_data_processor/json_processor.py",
        "instagram_data_processor/media_extractor.py",
        "instagram_data_processor/utils.py",
        "instagram_data_processor/exporters/__init__.py",
        "instagram_data_processor/exporters/txt_exporter.py",
        "instagram_data_processor/exporters/pdf_exporter.py",
        "instagram_data_processor/exporters/excel_exporter.py",
    ]
    
    all_files_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "OK" if exists else "MISSING"
        print(f"  {file_path}: {status}")
        if not exists:
            all_files_exist = False
    
    # Check if config.py exists, if not suggest copying from sample
    config_path = "instagram_data_processor/config.py"
    config_exists = os.path.exists(config_path)
    config_status = "OK" if config_exists else "MISSING"
    print(f"  {config_path}: {config_status}")
    
    if not config_exists:
        print("\nNOTE: Configuration file is missing. Please copy config_sample.py to instagram_data_processor/config.py and update it with your settings.")
    
    # Overall status
    print("\nOverall status:")
    if all_deps_installed and all_files_exist:
        print("✅ All checks passed! The Instagram Data Processor is correctly installed.")
        if not config_exists:
            print("   (You still need to set up the configuration file)")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above before running the processor.")
        return False

if __name__ == "__main__":
    main()
