from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="instagram-memory-book",
    version="1.0.0",
    author="Founas Mohamed Fares",
    author_email="fares.founas@example.com",
    description="Transform Instagram data exports into beautiful memory books",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fares303/Ai-instagram-message",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "emoji>=2.2.0",
        "fpdf2>=2.7.4",
        "matplotlib>=3.7.1",
        "numpy>=1.24.3",
        "openpyxl>=3.1.2",
        "pandas>=2.0.1",
        "Pillow>=9.5.0",
        "reportlab>=4.0.4",
    ],
    entry_points={
        "console_scripts": [
            "instagram-memory-book=run_processor:main",
        ],
    },
)
