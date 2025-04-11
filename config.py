import os

# Diretório para salvar arquivos temporários
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
OUTPUT_DIR = "output_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)