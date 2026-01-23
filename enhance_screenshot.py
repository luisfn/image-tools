#!/usr/bin/env python3
"""Enhance screenshots with browser frames and gradient backgrounds for social media."""

import argparse
import sys
from PIL import Image, ImageDraw, ImageFilter

GRADIENT_PRESETS = {
    "purple-blue": ((99, 58, 196), (41, 121, 255)),
    "blue-cyan": ((41, 121, 255), (0, 210, 211)),
    "pink-orange": ((233, 64, 127), (255, 154, 64)),
    "green-teal": ((22, 172, 93), (0, 194, 168)),
    "dark": ((30, 30, 40), (60, 60, 80)),
    "sunset": ((255, 95, 109), (255, 195, 113)),
}


def round_corners(image, radius):
    """Apply rounded corners to an image."""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    result = image.copy()
    result.putalpha(mask)
    return result


def add_browser_frame(screenshot, corner_radius=12):
    """Add a macOS-style browser chrome to the screenshot."""
    title_bar_height = 44
    width = screenshot.width
    total_height = screenshot.height + title_bar_height

    frame = Image.new("RGBA", (width, total_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(frame)

    # Title bar
    draw.rectangle([(0, 0), (width, title_bar_height)], fill=(243, 243, 243, 255))
    draw.line([(0, title_bar_height), (width, title_bar_height)], fill=(220, 220, 220, 255))

    # Traffic light dots
    dot_y = title_bar_height // 2
    dot_radius = 7
    dot_start_x = 20
    dot_spacing = 22

    colors = [(255, 95, 87), (255, 189, 46), (39, 201, 63)]
    for i, color in enumerate(colors):
        cx = dot_start_x + i * dot_spacing
        draw.ellipse(
            [(cx - dot_radius, dot_y - dot_radius), (cx + dot_radius, dot_y + dot_radius)],
            fill=color,
        )

    frame.paste(screenshot, (0, title_bar_height))
    frame = round_corners(frame, corner_radius)

    return frame


def create_gradient(width, height, color_start, color_end):
    """Create a diagonal gradient background."""
    try:
        import numpy as np

        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        xv, yv = np.meshgrid(x, y)
        factor = (xv + yv) / 2

        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for c in range(3):
            img_array[:, :, c] = (
                color_start[c] + (color_end[c] - color_start[c]) * factor
            ).astype(np.uint8)

        return Image.fromarray(img_array).convert("RGBA")
    except ImportError:
        # Fallback without numpy
        gradient = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(gradient)
        for y_pos in range(height):
            row_factor = y_pos / height
            for x_pos in range(width):
                factor = ((x_pos / width) + row_factor) / 2
                r = int(color_start[0] + (color_end[0] - color_start[0]) * factor)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * factor)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * factor)
                draw.point((x_pos, y_pos), fill=(r, g, b))
        return gradient.convert("RGBA")


def add_shadow(image, offset=(0, 12), blur_radius=40, shadow_color=(0, 0, 0, 80)):
    """Add a drop shadow behind the image."""
    shadow_size = (
        image.width + blur_radius * 2 + abs(offset[0]),
        image.height + blur_radius * 2 + abs(offset[1]),
    )

    shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
    shadow_shape = Image.new("RGBA", image.size, shadow_color)

    if image.mode == "RGBA":
        shadow_shape.putalpha(image.split()[3])

    shadow_x = blur_radius + max(0, offset[0])
    shadow_y = blur_radius + max(0, offset[1])
    shadow.paste(shadow_shape, (shadow_x, shadow_y))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    img_x = blur_radius + max(0, -offset[0])
    img_y = blur_radius + max(0, -offset[1])
    shadow.paste(image, (img_x, img_y), image)

    return shadow


def parse_color(color_str):
    """Parse a color string like '99,58,196' into a tuple."""
    parts = [int(x.strip()) for x in color_str.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Color must be R,G,B (e.g., '99,58,196')")
    return tuple(parts)


def enhance_screenshot(input_path, output_path, gradient_name="purple-blue",
                       color_start=None, color_end=None, padding=80,
                       corner_radius=12, no_frame=False, no_shadow=False):
    """Enhance a screenshot with frame, shadow, and gradient background."""
    screenshot = Image.open(input_path).convert("RGBA")
    print(f"Input: {screenshot.width}x{screenshot.height}")

    image = screenshot

    if not no_frame:
        image = add_browser_frame(image, corner_radius=corner_radius)

    if not no_shadow:
        image = add_shadow(image)

    # Resolve gradient colors
    if color_start and color_end:
        start, end = color_start, color_end
    else:
        start, end = GRADIENT_PRESETS[gradient_name]

    bg_width = image.width + padding * 2
    bg_height = image.height + padding * 2

    print(f"Generating gradient ({gradient_name})...")
    background = create_gradient(bg_width, bg_height, start, end)

    background.paste(image, (padding, padding), image)
    background.save(output_path, "PNG", optimize=True)
    print(f"Output: {output_path} ({bg_width}x{bg_height})")


def main():
    parser = argparse.ArgumentParser(
        description="Enhance screenshots for social media with browser frames and gradient backgrounds.",
    )
    parser.add_argument("input", nargs="?", help="Input screenshot path")
    parser.add_argument("output", nargs="?", default=None, help="Output path (default: input_enhanced.png)")
    parser.add_argument(
        "-g", "--gradient",
        choices=list(GRADIENT_PRESETS.keys()),
        default="purple-blue",
        help="Gradient preset (default: purple-blue)",
    )
    parser.add_argument("--color-start", type=parse_color, help="Custom start color as R,G,B")
    parser.add_argument("--color-end", type=parse_color, help="Custom end color as R,G,B")
    parser.add_argument("-p", "--padding", type=int, default=80, help="Padding around the image (default: 80)")
    parser.add_argument("-r", "--radius", type=int, default=12, help="Corner radius (default: 12)")
    parser.add_argument("--no-frame", action="store_true", help="Skip browser frame")
    parser.add_argument("--no-shadow", action="store_true", help="Skip drop shadow")
    parser.add_argument("--list-gradients", action="store_true", help="List available gradient presets")

    args = parser.parse_args()

    if args.list_gradients:
        print("Available gradient presets:")
        for name, (start, end) in GRADIENT_PRESETS.items():
            print(f"  {name:15s} {start} -> {end}")
        sys.exit(0)

    if not args.input:
        parser.error("input is required")

    if not args.output:
        from pathlib import Path
        p = Path(args.input)
        args.output = str(p.parent / f"{p.stem}_enhanced.png")

    enhance_screenshot(
        args.input,
        args.output,
        gradient_name=args.gradient,
        color_start=args.color_start,
        color_end=args.color_end,
        padding=args.padding,
        corner_radius=args.radius,
        no_frame=args.no_frame,
        no_shadow=args.no_shadow,
    )


if __name__ == "__main__":
    main()
