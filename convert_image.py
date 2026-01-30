#!/usr/bin/env python3
"""Convert images to different formats (e.g., PNG to WebP)."""

import argparse
import sys
import os
from pathlib import Path
from PIL import Image

def convert_image(input_path, output_path=None, format=None, quality=80):
    """
    Convert an image to a different format.
    
    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to the output image. If None, derived from input.
        format (str): Target format (e.g., 'webp', 'png', 'jpeg'). If None, derived from output extension.
        quality (int): Quality for lossy formats like JPEG or WebP (default: 80).
    """
    try:
        input_file = Path(input_path)
        
        if not input_file.exists():
            print(f"Error: Input file '{input_path}' not found.")
            sys.exit(1)

        # Open the image
        try:
            image = Image.open(input_path)
        except IOError:
            print(f"Error: Unable to open '{input_path}'. It might not be a valid image file.")
            sys.exit(1)

        # Determine output path if not provided
        if not output_path:
            # If format is provided, change extension. Otherwise default to webp as per user request example
            target_ext = f".{format.lower()}" if format else ".webp"
            output_path = input_file.with_suffix(target_ext)
        else:
            output_path = Path(output_path)
            # If format not explicitly given, try to guess from output filename
            if not format:
                # Remove leading dot
                format = output_path.suffix.lstrip('.')
                if not format:
                    format = "webp" # Default fallback
                    output_path = output_path.with_suffix(".webp")

        # Convert mode if necessary (e.g. RGBA to RGB for JPEG)
        target_format = (format or output_path.suffix.lstrip('.')).upper()
        
        if target_format == "JPG": 
            target_format = "JPEG"

        if target_format == "JPEG" and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Save the image
        print(f"Converting '{input_path}' to '{output_path}' (Format: {target_format})...")
        
        save_kwargs = {}
        if target_format in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality
            
        try:
            image.save(output_path, format=target_format, **save_kwargs)
            print(f"Success: Image saved to '{output_path}'")
        except KeyError:
            print(f"Error: Unknown or unsupported format '{target_format}'")
            sys.exit(1)
        except Exception as e:
            print(f"Error saving image: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Quickly convert images to different formats.",
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", nargs="?", help="Output image path (optional)")
    parser.add_argument("-f", "--format", help="Target format (e.g., webp, png, jpeg)")
    parser.add_argument("-q", "--quality", type=int, default=80, help="Quality (1-100) for lossy formats (default: 80)")

    args = parser.parse_args()

    convert_image(args.input, args.output, args.format, args.quality)

if __name__ == "__main__":
    main()
