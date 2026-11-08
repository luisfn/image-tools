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


def parse_ratio(ratio_str):
    """
    Parse a ratio string like '16:9' or '4:3' into a float (width/height).

    Args:
        ratio_str: String in the format 'W:H'

    Returns:
        float: The aspect ratio as width / height
    """
    parts = ratio_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid ratio format '{ratio_str}'. Use W:H (e.g. 16:9)")
    w, h = float(parts[0]), float(parts[1])
    if w <= 0 or h <= 0:
        raise ValueError("Ratio values must be positive numbers")
    return w / h


def apply_ratio(bbox, image_size, target_ratio):
    """
    Adjust a bounding box to match the target aspect ratio.

    First tries to expand the box. If the image is too small to fit the
    expanded dimension, shrinks the other dimension instead.

    Args:
        bbox: (left, upper, right, lower) bounding box
        image_size: (width, height) of the full image
        target_ratio: desired width/height ratio

    Returns:
        tuple: adjusted (left, upper, right, lower) bounding box
    """
    left, upper, right, lower = bbox
    img_w, img_h = image_size

    # Find the largest rectangle with the target ratio that fits in the image
    final_w = img_w
    final_h = int(img_w / target_ratio)
    if final_h > img_h:
        final_h = img_h
        final_w = int(img_h * target_ratio)

    # Center the box around the content center
    cx = (left + right) // 2
    cy = (upper + lower) // 2

    left = cx - final_w // 2
    right = left + final_w
    upper = cy - final_h // 2
    lower = upper + final_h

    # Clamp to image bounds, shifting if possible
    if left < 0:
        right = min(img_w, right - left)
        left = 0
    if upper < 0:
        lower = min(img_h, lower - upper)
        upper = 0
    if right > img_w:
        left = max(0, left - (right - img_w))
        right = img_w
    if lower > img_h:
        upper = max(0, upper - (lower - img_h))
        lower = img_h

    return (left, upper, right, lower)


def crop_image(input_path, output_path=None, padding=0, tolerance=10, ratio=None):
    """
    Auto-crop an image to its meaningful content area.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to the output image. If None, derived from input.
        padding (int): Extra padding around the detected content (default: 0).
        tolerance (int): Color tolerance for background detection (default: 10).
        ratio (str): Target aspect ratio in W:H format (e.g. '16:9'). Optional.
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

        # Apply aspect ratio if requested
        if ratio:
            target_ratio = parse_ratio(ratio)
            left, upper, right, lower = apply_ratio(
                (left, upper, right, lower), image.size, target_ratio
            )

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
    parser.add_argument("-r", "--ratio", type=str, default=None,
                        help="Target aspect ratio in W:H format (e.g. 16:9, 4:3, 1:1)")

    args = parser.parse_args()

    crop_image(args.input, args.output, args.padding, args.tolerance, args.ratio)


if __name__ == "__main__":
    main()
