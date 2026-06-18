#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [options] <links-file> [url1 url2 ...]

Download wallpaper images to a local directory.

Options:
  -o, --output DIR   Output directory (default: user wallpaper directory)
  -h, --help         Show this help message

Examples:
  $0 links.txtcd ~/Linux-type-wallpapers
chmod +x download_wallpapers.sh
./download_wallpapers.sh links.txt
EOF
  exit 1
}

get_default_output_dir() {
  if [[ -n "${HOME:-}" ]]; then
    output_dir="$HOME/Pictures/Wallpapers"
    if [[ -f "$HOME/.config/user-dirs.dirs" ]]; then
      picdir=$(grep '^XDG_PICTURES_DIR' "$HOME/.config/user-dirs.dirs" | head -n 1 | cut -d= -f2-)
      picdir=${picdir#\"}
      picdir=${picdir%\"}
      picdir=${picdir/#\$HOME/$HOME}
      if [[ -n "$picdir" ]]; then
        output_dir="$picdir/Wallpapers"
      fi
    fi
    printf '%s' "$output_dir"
  else
    printf '%s' "wallpapers"
  fi
}

output_dir="$(get_default_output_dir)"
links_file=""
urls=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      ;;
    -o|--output)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Error: missing argument for --output" >&2
        usage
      fi
      output_dir="$1"
      shift
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        urls+=("$1")
        shift
      done
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      ;;
    *)
      if [[ -z "$links_file" && -f "$1" ]]; then
        links_file="$1"
      else
        urls+=("$1")
      fi
      shift
      ;;
  esac
done

if [[ -n "$links_file" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line//[$'\t\r\n']/}"
    if [[ -n "$line" ]]; then
      urls+=("$line")
    fi
  done < "$links_file"
fi

if [[ ${#urls[@]} -eq 0 ]]; then
  echo "Error: no URLs provided." >&2
  usage
fi

mkdir -p "$output_dir"

download_cmd=""
if command -v curl >/dev/null 2>&1; then
  download_cmd="curl -L -sS -o"
elif command -v wget >/dev/null 2>&1; then
  download_cmd="wget -q -O"
else
  echo "Error: curl or wget is required to download wallpapers." >&2
  exit 1
fi

index=1
for url in "${urls[@]}"; do
  if [[ -z "$url" ]]; then
    continue
  fi

  filename=$(basename "${url%%\?*}")
  if [[ -z "$filename" || "$filename" =~ ^[[:space:]]*$ ]]; then
    filename="wallpaper_$index"
  fi

  if [[ ! "$filename" =~ \.[A-Za-z0-9]{2,5}$ ]]; then
    filename="${filename}.jpg"
  fi

  file_path="$output_dir/$filename"
  if [[ -e "$file_path" ]]; then
    base="${filename%.*}"
    ext="${filename##*.}"
    file_path="$output_dir/${base}_$index.$ext"
  fi

  echo "Downloading $url -> $file_path"
  if [[ "$download_cmd" == curl* ]]; then
    curl -L -sS -o "$file_path" "$url"
  else
    wget -q -O "$file_path" "$url"
  fi
  index=$((index + 1))
done

echo "Downloaded ${#urls[@]} wallpaper(s) to $output_dir."
echo "Check your wallpapers."
