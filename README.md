# Image Tool

An image converter tool for uncommon bitmap image conversions. The original goals of this are:

- Convert to ICO
- Convert to and from WEBP

## Supported Bitmap Files

The following file types are supported:

- PNG
- JPG
- WEBP
- ICO

### Making ICO Files

A dropdown menu is used to select what sizes to use in your ICO. In most cases, you should use the options labeled "Recommended" for your particular use case.

To convert to ICO, source images must have the same width and height, and must reach a minimum size depending on the output ICO sizes selected. The minimum dimensions required are:

- 32x32 (for "Minimum" preset) or 48x48 (for "Recommended" preset) for website favicon
- 256x256 for program icon

## Python Version

Use Python 3.13.
