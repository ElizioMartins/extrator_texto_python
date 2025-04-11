import os
from pathlib import Path
import win32com.client as win32
import pythoncom
import docx2txt
import fitz  # PyMuPDF
from docx import Document
from fastapi import UploadFile
from config import UPLOAD_DIR  # Importa o diretório de uploads


def convert_doc_to_docx(input_path: str) -> str | None:
    """Converte um arquivo .doc para .docx usando o Microsoft Word via COM."""
    input_path = os.path.abspath(input_path)

    if not os.path.exists(input_path):
        return None

    try:
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # Desativa alertas do Word

        doc = word.Documents.Open(input_path, ReadOnly=False, AddToRecentFiles=False)
        output_path = input_path + "x"  # "arquivo.doc" -> "arquivo.docx"
        doc.SaveAs(output_path, FileFormat=16)  # 16 = wdFormatDocumentDefault (DOCX)
        doc.Close()
        return output_path if os.path.exists(output_path) else None

    except Exception:
        return None

    finally:
        word.Quit()
        
def extract_text_from_docx(file_path: str) -> str:
    """Extrai texto de arquivos .docx"""
    return docx2txt.process(file_path)

def extract_text_from_pdf(file_path: str) -> str:
    """Extrai texto de arquivos PDF."""
    doc = fitz.open(file_path)
    return "\n".join([page.get_text("text") for page in doc])

async def process_uploaded_file(file: UploadFile) -> str | dict:
    """Processa o arquivo enviado e extrai o texto conforme a extensão."""
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
                os.remove(docx_path)
            else:
                return {"error": "Falha ao converter DOC para DOCX"}
        elif file_ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        else:
            return {"error": "Formato não suportado"}

        return text

    except Exception as e:
        return {"error": f"Erro ao processar arquivo: {str(e)}"}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def format_text(text: str) -> str:
    """Remove marcações ** de Markdown e converte \\n para quebras de linha reais."""
    text = text.replace("**", "")  # Remove negrito do Markdown
    text = text.replace("\\n", "\n")  # Converte para quebras de linha reais
    return text

def merge_text_with_docx(template_path: str, text: str, output_path: str):
    """Insere o texto no corpo de um modelo DOCX e salva como novo arquivo."""
    doc = Document(template_path)
    text = format_text(text)  # Formatar texto antes de inserir no DOCX
    
    # Adiciona o texto no corpo do documento
    doc.add_paragraph(text)
    
    doc.save(output_path)

