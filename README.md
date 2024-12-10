# PDFPageSlicer

PDFPageSlicer is a tool for extracting and processing regions from PDF documents based on bounding box coordinates. It's designed to make articles readable on small ereader screens. It can automatically subdivide tall regions into multiple pages with a specified aspect ratio.

## Features

- Extract specific regions from PDF pages using bounding box coordinates
- Automatically subdivide tall regions to maintain a desired aspect ratio
- Support for various aspect ratio formats (e.g., "3:4", "16/9", or decimal values)
- Combines all extracted regions into a single output PDF

## Prerequisites

The following dependencies are required:

- Python 3
- pdftk
- pdfcrop (part of texlive-extra-utils)
- poppler-utils
- mupdf-tools
- ghostscript

## Docker Usage

The easiest way to run PDFPageSlicer is using Docker:

```bash
# Build the Docker image
docker build -t PDFPageSlicer -f docker/Dockerfile .

# Run the container
docker run -v /path/to/your/pdfs:/pdfs PDFPageSlicer \
    /pdfs/input.pdf \
    /pdfs/annotations.json \
    /pdfs/output.pdf \
    --aspect-ratio 3:4
```


## Command Line Arguments

- `pdf_path`: Path to input PDF file
- `json_path`: Path to JSON file containing region annotations
- `output_path`: Destination path for the processed PDF
- `--aspect-ratio`: Target aspect ratio for subdivided regions (default: "3:4")
    - Accepts formats: "width:height", "width/height", or decimal value

## Example

```bash
python3 PDFPageSlicer/extract-regions.py \
    input.pdf \
    regions.json \
    output.pdf \
    --aspect-ratio 16:9
```

## Input Format

The tool expects a JSON file containing page numbers and their corresponding bounding boxes. The easiest way to create these is to use the provided gui tool. The format should be:

```json
{
    "0": [[x0, y0, x1, y1], [x0, y0, x1, y1], ...],
    "1": [[x0, y0, x1, y1], ...],
    ...
}
```

Where:
- Keys are page numbers (0-based)
- Values are lists of bounding boxes for that page
- Each bounding box is specified as [x0, y0, x1, y1] coordinates
