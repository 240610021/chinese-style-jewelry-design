import os
import subprocess
import sys

HTML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "应聘补充资料")
PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "应聘补充资料_PDF")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def html_to_pdf(html_path: str, pdf_path: str):
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        f"file:///{html_path.replace(os.sep, '/')}",
    ]
    print(f"Processing: {os.path.basename(html_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  -> Error: {result.stderr}", file=sys.stderr)
    else:
        print(f"  -> Done: {os.path.basename(pdf_path)}")

def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(HTML_DIR) if f.endswith(".html")])
    print(f"Found {len(files)} HTML files")
    for fname in files:
        html_path = os.path.join(HTML_DIR, fname)
        pdf_path = os.path.join(PDF_DIR, fname.replace(".html", ".pdf"))
        html_to_pdf(html_path, pdf_path)
    print("All PDFs generated.")

if __name__ == "__main__":
    main()
