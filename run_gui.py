"""
Launcher script for the Instagram Memory Book Generator GUI.
"""

import sys
import os

# Add the parent directory to sys.path to allow importing the package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the GUI application
from instagram_data_processor.gui_app import main

if __name__ == "__main__":
    main()
