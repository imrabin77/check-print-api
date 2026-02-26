#!/usr/bin/env bash
set -e

# Install Tesseract OCR and Poppler (for PDF)
apt-get update && apt-get install -y tesseract-ocr poppler-utils

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
