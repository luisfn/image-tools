# Image Tools

A collection of CLI tools for enhancing images for social media and presentations.

## Setup

### Local Installation

```bash
pip3 install -r requirements.txt
```

### Docker

Build the image:

```bash
make build
```

Run tools using make targets:

```bash
make enhance INPUT=<file> [OUTPUT=<file>] [ARGS="..."]
make remove-bg INPUT=<file> [OUTPUT=<file>] [ARGS="..."]
make vectorize INPUT=<file> [OUTPUT=<file>] [ARGS="..."]
make convert INPUT=<file> [OUTPUT=<file>] [ARGS="..."]
```

**Examples:**

```bash
# Enhance a screenshot with default settings
make enhance INPUT=~/Desktop/screenshot.png

# Enhance with sunset gradient and extra padding
make enhance INPUT=~/Desktop/screenshot.png ARGS="-g sunset -p 120"

# Enhance with custom output path
make enhance INPUT=~/Desktop/screenshot.png OUTPUT=~/Desktop/fancy.png

# Remove background from a photo (AI-based)
make remove-bg INPUT=~/Photos/portrait.jpg

# Remove solid color background from a logo
make remove-bg INPUT=./logo.png ARGS="--color 255,255,255"

# Convert PNG logo to vector SVG
make vectorize INPUT=~/Desktop/logo.png

# Convert to black & white vector
make vectorize INPUT=~/Desktop/logo.png OUTPUT=~/Desktop/logo.svg ARGS="--binary"

# Convert image to WebP format
make convert INPUT=./photo.png

# Convert to JPEG with high quality
make convert INPUT=./photo.png OUTPUT=./photo.jpg ARGS="-f jpeg -q 95"
```

Remove the Docker image:

```bash
make clean
```

## Tools

### enhance_screenshot.py

Adds a macOS-style browser frame, drop shadow, and gradient background to screenshots.

**Usage:**

```bash
python3 enhance_screenshot.py <input> [output] [options]
```

If no output path is provided, saves as `<input_name>_enhanced.png`.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-g`, `--gradient` | Gradient preset name | `purple-blue` |
| `--color-start` | Custom start color (R,G,B) | — |
| `--color-end` | Custom end color (R,G,B) | — |
| `-p`, `--padding` | Padding around image in px | `80` |
| `-r`, `--radius` | Corner radius in px | `12` |
| `--no-frame` | Skip browser frame | — |
| `--no-shadow` | Skip drop shadow | — |
| `--list-gradients` | Show available presets | — |

**Gradient Presets:**

| Name | Colors |
|------|--------|
| `purple-blue` | Purple to Blue |
| `blue-cyan` | Blue to Cyan |
| `pink-orange` | Pink to Orange |
| `green-teal` | Green to Teal |
| `dark` | Dark Gray |
| `sunset` | Red to Yellow |

**Examples:**

```bash
# Default style
python3 enhance_screenshot.py screenshot.png

# Specific output path
python3 enhance_screenshot.py screenshot.png social_post.png

# Sunset gradient with extra padding
python3 enhance_screenshot.py screenshot.png -g sunset -p 120

# Custom gradient colors
python3 enhance_screenshot.py screenshot.png --color-start 20,20,40 --color-end 60,60,120

# Just gradient background, no browser frame
python3 enhance_screenshot.py screenshot.png --no-frame

# No shadow
python3 enhance_screenshot.py screenshot.png --no-shadow
```

### convert_image.py

Quickly convert images between different formats (e.g., PNG to WebP).

**Usage:**

```bash
./convert_image.py <input> [output] [options]
```

If no output path or format is provided, it defaults to converting to WebP and saves as `<input_name>.webp`.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-f`, `--format` | Target format (webp, png, jpeg) | `webp` (if no output) |
| `-q`, `--quality` | Quality (1-100) for lossy formats | `80` |

**Examples:**

```bash
# Convert to WebP (default)
./convert_image.py image.png

# Convert to specific format
./convert_image.py image.png -f jpeg

# Convert with specific output name
./convert_image.py image.png final_version.webp

# Convert with high quality
./convert_image.py photo.png -f webp -q 95
```

### remove_bg.py

Removes backgrounds from images, making them transparent. Supports AI-based removal for photos or color-based removal for logos with solid backgrounds.

**Usage:**

```bash
python3 remove_bg.py <input> [options]
```

If no output path is provided, saves as `<input_name>_transparent.png`.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output file path | `<input>_transparent.png` |
| `-c`, `--color` | Remove specific color (R,G,B) | — (uses AI) |
| `-t`, `--tolerance` | Color tolerance for matching | `30` |

**Examples:**

```bash
# AI-based removal (for photos)
python3 remove_bg.py photo.jpg

# Remove solid color background (for logos)
python3 remove_bg.py logo.png --color 255,204,0

# With higher tolerance for color variations
python3 remove_bg.py logo.png --color 255,204,0 --tolerance 50

# Specify output path
python3 remove_bg.py photo.jpg -o photo_nobg.png
```

### vectorize_image.py

Converts raster images (PNG, JPG, etc.) to SVG vector format.

**Usage:**

```bash
python3 vectorize_image.py <input> [options]
```

If no output path is provided, saves as `<input_name>.svg`.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output file path | `<input>.svg` |
| `-b`, `--binary` | Binary (black & white) mode | — |
| `-p`, `--precision` | Color precision 1-8 | `6` |
| `-s`, `--speckle` | Filter speckle size | `4` |

**Examples:**

```bash
# Basic vectorization
python3 vectorize_image.py logo.png

# Black & white mode
python3 vectorize_image.py logo.png --binary

# Fine-tune for detailed images
python3 vectorize_image.py logo.png --speckle 1 --precision 8

# Specify output path
python3 vectorize_image.py logo.png -o logo_vector.svg
```

## Requirements

- Python 3.8+
- Pillow
- numpy (optional, speeds up gradient generation)
- rembg (for AI background removal in remove_bg.py)
- vtracer (for vectorize_image.py)
