# Typography Reference Guide

## Font Metrics

### Basic Measurements
- **x-height**: Height of lowercase 'x' character
- **Cap height**: Height of capital letters
- **Ascender**: Part of letter extending above x-height
- **Descender**: Part of letter extending below baseline
- **Line height**: Total vertical space including leading

### Font Size Conversions
- 1 point = 1.333 pixels (at 96 DPI)
- 1 em = current font size
- 1 rem = root element font size
- Default browser font: 16px = 12pt

## Common Font Families

### System Fonts
- **Windows**: Segoe UI, Tahoma, Arial
- **macOS**: San Francisco, Helvetica Neue
- **Linux**: Ubuntu, DejaVu Sans, Liberation Sans
- **Android**: Roboto, Noto Sans
- **iOS**: San Francisco, Helvetica Neue

### Web-Safe Font Stacks
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
font-family: Georgia, "Times New Roman", Times, serif;
font-family: "Courier New", Courier, monospace;
```

## Font Weight Mappings
- 100: Thin/Hairline
- 200: Extra Light
- 300: Light
- 400: Normal/Regular
- 500: Medium
- 600: Semi Bold
- 700: Bold
- 800: Extra Bold
- 900: Black/Heavy

## Text Measurement Calculations

### Line Height Ratios
- Body text: 1.4-1.6
- Headlines: 1.1-1.3
- Captions: 1.3-1.4

### Letter Spacing
- Normal: 0
- Tight: -0.025em to -0.05em
- Loose: 0.025em to 0.1em

### Optimal Line Length
- 45-75 characters per line
- 50-60 characters ideal for readability
