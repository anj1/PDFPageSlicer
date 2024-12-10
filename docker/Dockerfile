# Use Ubuntu as the base image
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    texlive-extra-utils \
    pdftk \
    poppler-utils \
    mupdf-tools \
    ghostscript \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pymupdf package using pip3
RUN pip3 install pymupdf

# Create working directory
RUN mkdir -p /pdfs
WORKDIR /app

# Copy the application code
COPY pageslicer /app/pageslicer
COPY tools /app/tools

# Make the Python script executable
RUN chmod +x /app/pageslicer/extract-regions.py

# Set the entry point to run the Python script
ENTRYPOINT ["python3", "/app/pageslicer/extract-regions.py"]

# Create a volume for PDF files
VOLUME ["/pdfs"]