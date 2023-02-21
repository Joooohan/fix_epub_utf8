import argparse
import os
import tempfile
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str)
parser.add_argument("-o", "--output", type=str)
args = parser.parse_args()
print(args)

# Analyze arguments
if args.filename is None:
    raise ValueError("No input file specified.")

file_path = Path(args.filename)

if not file_path.exists():
    raise ValueError(f"The specified file does not exist: {file_path}")

if args.output is None:
    out_path = file_path.parent / f"{file_path.stem}_utf8{file_path.suffix}"
else:
    out_path = Path(args.output)

if out_path.exists():
    raise ValueError(f"The speficied output exists: {out_path}")

with tempfile.TemporaryDirectory() as tmp_dir:
    folder_path = Path(tmp_dir)

    # Extract EPUB
    with zipfile.ZipFile(file_path, "r") as book:
        book.extractall(folder_path)

    # Edit XHTML files: add meta tag to specify utf-8 encoding
    candidates = [
        os.path.join("OPS", "xhtml"),
        os.path.join("OEBPS", "xhtml"),
        os.path.join("OEBPS", "Text"),
        "text",
    ]
    for candidate in candidates:
        xml_folder = folder_path / candidate
        if xml_folder.exists():
            break

    if not xml_folder.exists():
        raise FileNotFoundError(
            f"Content folder not found in {os.listdir(folder_path)}"
        )

    for file_name in os.listdir(xml_folder):
        xml_path = xml_folder / file_name
        with open(xml_path) as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        meta = soup.new_tag("meta")
        meta["http-equiv"] = "Content-Type"
        meta["content"] = "text/html; charset=utf-8"
        soup.head.append(meta)

        with open(xml_path, "wb") as f:
            f.write(soup.encode("utf8"))

    # Write output file
    with zipfile.ZipFile(out_path, "w") as new_book:
        # `mimetype` should be written first without compression
        arcname = "mimetype"
        mime_file = folder_path / arcname
        with open(mime_file, "rb") as f:
            new_book.writestr(arcname, f.read())

        for root, _, f_names in os.walk(folder_path):
            root = Path(root)
            if root == folder_path:
                continue

            relative_root = Path(root).relative_to(folder_path)
            for f_name in f_names:
                f_path = root / f_name
                arcname = relative_root / f_name
                with open(f_path, "rb") as f:
                    new_book.writestr(
                        str(arcname),
                        f.read(),
                        compress_type=zipfile.ZIP_DEFLATED,
                    )
