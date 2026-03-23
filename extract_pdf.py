import sys
import subprocess
try:
    import pypdf
except ImportError:
    print("Installing pypdf...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

pdf_path = "c:\\Users\\enzos\\Documents\\GitHub\\Docs-SISR\\B2-Act9-TP1 Monter son serveur de mails.pdf"
try:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for i, page in enumerate(reader.pages):
        text += f"--- Page {i+1} ---\n"
        text += page.extract_text() + "\n"
        
    with open("c:\\Users\\enzos\\Documents\\GitHub\\Docs-SISR\\pdf_text_extracted.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully extracted text to pdf_text_extracted.txt")
except Exception as e:
    print(f"Error: {e}")
