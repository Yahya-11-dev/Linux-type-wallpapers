#!/usr/bin/env python3
import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def default_output_dir():
    home = os.path.expanduser("~")
    output_dir = os.path.join(home, "Pictures", "Wallpapers")
    if os.name != "nt":
        config_path = os.path.join(home, ".config", "user-dirs.dirs")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as handle:
                    for line in handle:
                        line = line.strip()
                        if line.startswith("XDG_PICTURES_DIR"):
                            _, value = line.split("=", 1)
                            value = value.strip().strip('"')
                            value = value.replace("$HOME", home)
                            output_dir = os.path.expandvars(value)
                            output_dir = os.path.join(output_dir, "Wallpapers")
                            break
            except OSError:
                pass
    return output_dir


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download wallpaper images from URLs or a links file."
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="One or more direct image URLs.",
    )
    parser.add_argument(
        "-f",
        "--links-file",
        help="Text file containing one image URL per line.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=default_output_dir(),
        help="Output directory for downloaded images. Default is the user wallpaper directory.",
    )
    parser.add_argument(
        "--set",
        action="store_true",
        help="On Windows, set the last downloaded image as the desktop wallpaper.",
    )
    return parser.parse_args()


def sanitize_filename(url, index):
    parsed = urllib.parse.urlparse(url)
    name = os.path.basename(parsed.path)
    if not name or name.endswith("/"):
        name = f"wallpaper_{index}.jpg"
    if not os.path.splitext(name)[1]:
        name += ".jpg"
    return name


def download_image(url, output_dir, index):
    filename = sanitize_filename(url, index)
    file_path = os.path.join(output_dir, filename)
    original_path = file_path
    counter = 1
    while os.path.exists(file_path):
        base, ext = os.path.splitext(original_path)
        file_path = f"{base}_{counter}{ext}"
        counter += 1

    try:
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded {url} -> {file_path}")
        return file_path
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Failed to download {url}: {exc}", file=sys.stderr)
        return None


def load_links_from_file(path):
    urls = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def set_windows_wallpaper(image_path):
    try:
        import ctypes
        if os.name != "nt":
            print("Wallpaper setting is only supported on Windows.")
            return False
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            image_path,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE,
        )
        if not result:
            print("Failed to set Windows wallpaper.")
            return False
        print(f"Wallpaper set to {image_path}")
        return True
    except Exception as exc:
        print(f"Error setting wallpaper: {exc}", file=sys.stderr)
        return False


def main():
    args = parse_args()
    urls = list(args.urls)

    if args.links_file:
        urls.extend(load_links_from_file(args.links_file))

    if not urls:
        print("No URLs provided. Use --links-file or pass URLs on the command line.")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    downloaded = []

    for index, url in enumerate(urls, start=1):
        result = download_image(url, args.output, index)
        if result:
            downloaded.append(result)

    if not downloaded:
        print("No wallpapers were downloaded.")
        sys.exit(1)

    print(f"Downloaded {len(downloaded)} wallpaper(s) to {args.output}.")
    print("Check your wallpapers.")

    if args.set:
        last_image = downloaded[-1]
        set_windows_wallpaper(os.path.abspath(last_image))


if __name__ == "__main__":
    main()
