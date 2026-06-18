# Linux-type-wallpapers

Utility scripts for downloading wallpaper images from URL links.

## Files

- `download_wallpapers.sh` — Linux shell script to download images to the user wallpaper directory by default.
- `download_wallpapers.py` — Windows Python script to download images to the user wallpaper directory by default and optionally set the desktop wallpaper.

## Usage

### Linux

1. Make the script executable:

   ```bash
   chmod +x download_wallpapers.sh
   ```

2. Run the script with a file of URLs or direct links:

   ```bash
   ./download_wallpapers.sh links.txt
   ./download_wallpapers.sh -o wallpapers https://example.com/image1.jpg https://example.com/image2.png
   ```

### Windows

1. Install Python 3 if needed.
2. Run the script with a links file or URLs:

   ```powershell
   python download_wallpapers.py -f links.txt
   python download_wallpapers.py https://example.com/image1.jpg https://example.com/image2.png
   ```

3. Optionally set the last downloaded image as the Windows wallpaper:

   ```powershell
   python download_wallpapers.py -f links.txt --set
   ```

## Links file format

Use one URL per line. Lines beginning with `#` are ignored.
