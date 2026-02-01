#!/usr/bin/env python3
"""Convert raster images to SVG vector format."""

import argparse
import sys
from pathlib import Path


def vectorize_image(input_path, output_path, color_mode="color", color_precision=6,
                    filter_speckle=4, corner_threshold=60, simplify=True):
    """Convert a raster image to SVG vector format."""
    try:
        import vtracer
    except ImportError:
        print("Error: vtracer is required for vectorization.")
        print("Install it with: pip install vtracer")
        sys.exit(1)

    from PIL import Image
    import tempfile

    input_path = str(Path(input_path).expanduser().resolve())
    output_path = str(Path(output_path).expanduser().resolve())

    print(f"Vectorizing '{input_path}'...")

    # Normalize via Pillow to handle format/extension mismatches
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        img = Image.open(input_path)
        img.save(tmp_path, "PNG")

        vtracer.convert_image_to_svg_py(
            tmp_path,
            output_path,
            colormode=color_mode,
            hierarchical="stacked",
            mode="spline",
            filter_speckle=filter_speckle,
            color_precision=color_precision,
            layer_difference=16,
            corner_threshold=corner_threshold,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if simplify:
        _simplify_svg(output_path)

    print(f"Success: Saved to '{output_path}'")


def _simplify_svg(svg_path):
    """Remove unnecessary whitespace from SVG."""
    try:
        import re
        with open(svg_path, "r") as f:
            content = f.read()
        content = re.sub(r">\s+<", "><", content)
        with open(svg_path, "w") as f:
            f.write(content)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Convert raster images to SVG vectors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic vectorization
  %(prog)s logo.png

  # Black & white mode
  %(prog)s --binary logo.png

  # Fine-tune for detailed images
  %(prog)s --speckle 1 --precision 8 logo.png
"""
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output path (default: input.svg)")
    parser.add_argument("-b", "--binary", action="store_true",
                        help="Binary (black & white) mode")
    parser.add_argument("-p", "--precision", type=int, default=6,
                        help="Color precision 1-8 (default: 6)")
    parser.add_argument("-s", "--speckle", type=int, default=4,
                        help="Filter speckle size (default: 4)")

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_path = input_path.parent / f"{input_path.stem}.svg"

    color_mode = "binary" if args.binary else "color"
    vectorize_image(
        str(input_path),
        str(output_path),
        color_mode=color_mode,
        color_precision=args.precision,
        filter_speckle=args.speckle,
    )


if __name__ == "__main__":
    main()
