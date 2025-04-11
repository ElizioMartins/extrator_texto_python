from fastapi import FastAPI, File, UploadFile
import os
import fitz  # pymupdf para PDF
import docx2txt
import pythoncom
import win32com.client as win32
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def convert_doc_to_docx(input_path: str) -> str | None:
    """Converte um arquivo .doc para .docx usando o Microsoft Word via COM."""
    pythoncom.CoInitialize()
    input_path = os.path.abspath(input_path)  # Garante caminho absoluto

    if not os.path.exists(input_path):
        return None  # Evita retornar string como erro

    try:
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # Desativa alertas do Word

        doc = word.Documents.Open(input_path, ReadOnly=False, AddToRecentFiles=False)
        output_path = input_path + "x"  # Converte "arquivo.doc" para "arquivo.docx"
        doc.SaveAs(output_path, FileFormat=16)  # 16 = wdFormatDocumentDefault (DOCX)
        doc.Close()
        return output_path if os.path.exists(output_path) else None

    except Exception as e:
        return None  # Retorna None se falhar

    finally:
        word.Quit()  # Garante fechamento do Word

def extract_text_from_docx(file_path: str) -> str:
    """Extrai texto de arquivos .docx"""
    return docx2txt.process(file_path)

def extract_text_from_pdf(file_path: str) -> str:
    """Extrai texto de arquivos PDF."""
    doc = fitz.open(file_path)
    return "\n".join([page.get_text("text") for page in doc])

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        if file_ext == ".docx":
            text = extract_text_from_docx(file_path)
        elif file_ext == ".doc":
            docx_path = convert_doc_to_docx(file_path)
            if docx_path and os.path.exists(docx_path):
                text = extract_text_from_docx(docx_path)
                os.remove(docx_path)  # Remove arquivo convertido
            else:
                return {"error": "Falha ao converter DOC para DOCX"}
        elif file_ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        else:
            return {"error": "Formato não suportado"}

        return {"text": text}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
