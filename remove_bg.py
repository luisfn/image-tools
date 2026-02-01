#!/usr/bin/env python3
"""Remove backgrounds from images to make them transparent."""

import argparse
import sys
from pathlib import Path


def remove_background(input_path, output_path, color=None, tolerance=30):
    """Remove the background from an image, making it transparent."""
    from PIL import Image

    # Ensure absolute paths
    input_path = str(Path(input_path).expanduser().resolve())
    output_path = str(Path(output_path).expanduser().resolve())

    print(f"Removing background from '{input_path}'...")

    if color:
        # Color-based removal (better for logos with solid backgrounds)
        img = Image.open(input_path).convert("RGBA")
        data = img.getdata()

        new_data = []
        for pixel in data:
            r, g, b, a = pixel
            if (abs(r - color[0]) <= tolerance and
                abs(g - color[1]) <= tolerance and
                abs(b - color[2]) <= tolerance):
                new_data.append((r, g, b, 0))
            else:
                new_data.append(pixel)

        img.putdata(new_data)
        img.save(output_path, "PNG")
    else:
        # AI-based removal (better for photos)
        try:
            from rembg import remove
        except ImportError:
            print("Error: rembg is required for AI background removal.")
            print("Install it with: pip install rembg[cpu]")
            print("Or use --color for solid color backgrounds.")
            sys.exit(1)

        with open(input_path, "rb") as f:
            input_data = f.read()

        output_data = remove(input_data)

        with open(output_path, "wb") as f:
            f.write(output_data)

    print(f"Success: Saved to '{output_path}'")


def main():
    parser = argparse.ArgumentParser(
        description="Remove backgrounds from images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AI-based removal (for photos)
  %(prog)s photo.jpg

  # Remove solid color background (for logos)
  %(prog)s --color 255,204,0 logo.png

  # With higher tolerance for color variations
  %(prog)s --color 255,204,0 --tolerance 50 logo.png
"""
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output path (default: input_transparent.png)")
    parser.add_argument("-c", "--color", type=str, metavar="R,G,B",
                        help="Remove specific color (e.g., '255,204,0' for yellow)")
    parser.add_argument("-t", "--tolerance", type=int, default=30,
                        help="Color tolerance (default: 30)")

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_path = input_path.parent / f"{input_path.stem}_transparent.png"

    bg_color = None
    if args.color:
        bg_color = tuple(int(x.strip()) for x in args.color.split(","))

    remove_background(str(input_path), str(output_path), color=bg_color, tolerance=args.tolerance)


if __name__ == "__main__":
    main()
