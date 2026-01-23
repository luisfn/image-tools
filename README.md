# Image Tools

A collection of CLI tools for enhancing images for social media and presentations.

## Setup

```bash
pip3 install -r requirements.txt
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

## Requirements

- Python 3.8+
- Pillow
- numpy (optional, speeds up gradient generation)
