#!/usr/bin/env python3
"""Auto-crop images by detecting the meaningful content area."""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageChops


def detect_background_color(image):
    """
    Detect the background color by sampling corner pixels.

    Args:
        image: PIL Image object

    Returns:
        tuple: The most common corner color (R, G, B) or (R, G, B, A)
    """
    width, height = image.size

    # Sample pixels from all four corners
    corners = [
        image.getpixel((0, 0)),
        image.getpixel((width - 1, 0)),
        image.getpixel((0, height - 1)),
        image.getpixel((width - 1, height - 1)),
    ]

    # Return the most common corner color
    return max(set(corners), key=corners.count)


def get_content_bbox(image, tolerance=0):
    """
    Get the bounding box of the meaningful content in an image.

    For images with transparency, finds non-transparent pixels.
    For opaque images, finds pixels different from the background color.

    Args:
        image: PIL Image object
        tolerance: Color difference tolerance for background detection

    Returns:
        tuple: (left, upper, right, lower) bounding box, or None if empty
    """
    # If image has alpha channel, try to use it for detection
    if image.mode in ('RGBA', 'LA'):
        # Get the alpha channel
        if image.mode == 'RGBA':
            alpha = image.split()[3]
        else:
            alpha = image.split()[1]

        # Check if there's actual transparency variation (not all opaque)
        alpha_extrema = alpha.getextrema()
        if alpha_extrema[0] < 255:  # Has some transparency
            # Get bounding box of non-transparent pixels
            bbox = alpha.point(lambda x: 255 if x > 0 else 0).getbbox()
            if bbox:
                return bbox

    # For images without useful alpha (or all opaque), detect background color
    bg_color = detect_background_color(image)

    # Create a solid background image
    bg = Image.new(image.mode, image.size, bg_color)

    # Find difference between image and background
    diff = ImageChops.difference(image, bg)

    # If there's a tolerance, apply threshold
    if tolerance > 0:
        # Convert to grayscale for easier thresholding
        diff_gray = diff.convert('L')
        diff = diff_gray.point(lambda x: 255 if x > tolerance else 0)

    return diff.getbbox()


def crop_image(input_path, output_path=None, padding=0, tolerance=10):
    """
    Auto-crop an image to its meaningful content area.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to the output image. If None, derived from input.
        padding (int): Extra padding around the detected content (default: 0).
        tolerance (int): Color tolerance for background detection (default: 10).
    """
    try:
        input_file = Path(input_path).expanduser()

        if not input_file.exists():
            print(f"Error: Input file '{input_path}' not found.")
            sys.exit(1)

        # Open the image
        try:
            image = Image.open(input_file)
        except IOError:
            print(f"Error: Unable to open '{input_path}'. It might not be a valid image file.")
            sys.exit(1)

        # Determine output path if not provided
        if not output_path:
            output_path = input_file.parent / f"{input_file.stem}_cropped.png"
        else:
            output_path = Path(output_path).expanduser()

        # Get the bounding box of the content
        bbox = get_content_bbox(image, tolerance)

        if not bbox:
            print("Warning: No content detected. Saving original image.")
            image.save(output_path, "PNG")
            print(f"Success: Image saved to '{output_path}'")
            return

        # Apply padding
        left, upper, right, lower = bbox
        width, height = image.size

        left = max(0, left - padding)
        upper = max(0, upper - padding)
        right = min(width, right + padding)
        lower = min(height, lower + padding)

        # Crop the image
        cropped = image.crop((left, upper, right, lower))

        # Report crop results
        original_size = f"{width}x{height}"
        new_size = f"{right - left}x{lower - upper}"
        print(f"Cropping '{input_path}' from {original_size} to {new_size}...")

        # Preserve format or default to PNG
        output_format = output_path.suffix.lstrip('.').upper() or 'PNG'
        if output_format == 'JPG':
            output_format = 'JPEG'

        # Convert if saving to JPEG
        if output_format == 'JPEG' and cropped.mode in ('RGBA', 'LA', 'P'):
            cropped = cropped.convert('RGB')

        cropped.save(output_path, format=output_format)
        print(f"Success: Image saved to '{output_path}'")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-crop images by detecting the meaningful content area.",
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", nargs="?", help="Output image path (optional)")
    parser.add_argument("-p", "--padding", type=int, default=0,
                        help="Extra padding around detected content in px (default: 0)")
    parser.add_argument("-t", "--tolerance", type=int, default=10,
                        help="Color tolerance for background detection (default: 10)")

    args = parser.parse_args()

    crop_image(args.input, args.output, args.padding, args.tolerance)


if __name__ == "__main__":
    main()
