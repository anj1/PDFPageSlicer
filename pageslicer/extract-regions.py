import json
import subprocess
import tempfile
import os
from pathlib import Path

def subdivide_bbox(bbox, aspect_ratio):
    top = bbox[3]
    bottom = bbox[1]
    width = bbox[2] - bbox[0]
    height = width/aspect_ratio

    if height > (top - bottom):
        return [bbox]

    rn = []
    for y in range(int(top), int(bottom), -int(height)):
        if (y - height) < bottom:
            rn.append([bbox[0], bottom, bbox[2], bottom + height])
        else:
            rn.append([bbox[0], y - height, bbox[2], y])

    return rn 

def extract_regions(pdf_path, json_path, output_path, aspect_ratio=0.725):
    with open(json_path) as f:
        annotations = json.load(f)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        extracted_pdfs = []
        
        for page_num, boxes in annotations.items():
            page_num = int(page_num)
            
            # First extract the page
            page_pdf = os.path.join(tmpdir, f'page_{page_num}.pdf')
            subprocess.run(['pdftk', pdf_path, 'cat', f'{page_num + 1}', 'output', page_pdf], check=True)
            
            for box_idx, box in enumerate(boxes):
                # Get subdivisions
                sub_boxes = subdivide_bbox(box, aspect_ratio)
                
                for sub_idx, sub_box in enumerate(sub_boxes):
                    x0, y0, x1, y1 = sub_box
                    
                    # Extract and crop region
                    bbox = f'{x0} {y0} {x1} {y1}'
                    output_path_temp = os.path.join(tmpdir, f'region_{page_num}_{box_idx}_{sub_idx}.pdf')
                    cmd = ['pdfcrop', '--bbox', bbox, page_pdf, output_path_temp]
                    subprocess.run(cmd, check=True)
                    
                    extracted_pdfs.append(output_path_temp)
        
        # Merge all extracted PDFs
        subprocess.run(['pdftk'] + extracted_pdfs + ['cat', 'output', output_path], check=True)

def parse_aspect_ratio(ratio_str):
    """Convert aspect ratio string like '3:4' or '16/9' to float"""
    try:
        if ':' in ratio_str:
            width, height = map(float, ratio_str.split(':'))
        elif '/' in ratio_str:
            width, height = map(float, ratio_str.split('/'))
        else:
            # If it's already a decimal number, just convert it
            return float(ratio_str)
        
        if height == 0:
            raise ValueError("Height cannot be zero")
        return width / height
        
    except (ValueError, TypeError) as e:
        raise argparse.ArgumentTypeError(
            f"Invalid aspect ratio format: {ratio_str}. Use formats like '3:4', '16/9', or '0.75'"
        )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_path', help='Path to input PDF')
    parser.add_argument('json_path', help='Path to JSON file with annotations')
    parser.add_argument('output_path', help='Path for output PDF')
    # add argument for aspect ratio
    parser.add_argument('--aspect-ratio', type=parse_aspect_ratio, default='3:4', help='Aspect ratio for subregions (e.g. "3:4", "16/9", or "0.75". Default: 3:4)')

    args = parser.parse_args()
    
    # make sure aspect ratio isn't too small
    if args.aspect_ratio < 0.01:
        parser.error("Aspect ratio is too small")

    extract_regions(args.pdf_path, args.json_path, args.output_path, args.aspect_ratio)