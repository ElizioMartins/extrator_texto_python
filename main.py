import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
import pythoncom
from utils import process_uploaded_file, merge_text_with_docx
from config import UPLOAD_DIR , OUTPUT_DIR
from fastapi.responses import FileResponse
from fastapi import Form


app = FastAPI()

pythoncom.CoInitialize()  # Inicializa a comunicação com o Word COM



@app.post("/extract-text/{tipo}/")
async def extract_text(tipo: str, file: UploadFile = File(...)):
    """
    Extrai texto de arquivos DOC, DOCX ou PDF.
    O `tipo` define se o retorno será {"edital": texto} ou {"ata": texto}.
    """
    resultado = await process_uploaded_file(file)
    if isinstance(resultado, dict):  # Verifica se houve erro
        return resultado

    return {tipo: resultado}

@app.post("/merge-docx/")
async def merge_docx(text: str = Form(...)):
    """Carrega o modelo TemplateAta.docx, insere o texto e retorna o novo arquivo para download."""
    template_path = os.path.join("input_docs", "TemplateAta.docx")
    output_path = os.path.join(OUTPUT_DIR, "documento_final.docx")

    if not os.path.exists(template_path):
        return {"error": "Arquivo TemplateAta.docx não encontrado na pasta input_docs."}

    try:
        merge_text_with_docx(template_path, text, output_path)
        return FileResponse(output_path, filename="documento_final.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        return {"error": str(e)}

# POCO nesse modelo o aruivo é enviado via POST e o texto é enviado via Form
# @app.post("/merge-docx/")
# async def merge_docx(file: UploadFile = File(...), text: str = Form(...)):

    """Recebe um modelo DOCX e um texto, insere o texto e retorna o novo arquivo para download."""
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext != ".docx":
        return {"error": "Formato não suportado. Envie um arquivo DOCX."}

    template_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(OUTPUT_DIR, "documento_final.docx")

    with open(template_path, "wb") as f:
        f.write(await file.read())

    try:
        merge_text_with_docx(template_path, text, output_path)
        return FileResponse(output_path, filename="documento_final.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(template_path):
            os.remove(template_path)