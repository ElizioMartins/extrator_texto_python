📄 Extrator de Texto Python
Este projeto é um serviço FastAPI para extrair texto de arquivos DOC, DOCX e PDF e gerar atas editadas com um modelo pré-definido.

🛠 Instalação
Instale as dependências do Python:
pip install -r requirements.txt

Inicie o servidor FastAPI:
uvicorn main:app --host 0.0.0.0 --port 8000

Configure o acesso externo com Ngrok:
ngrok http 8000

🔗 Integração com o n8n
Como o endereço do servidor pode mudar ao usar o Ngrok, é necessário atualizar o endpoint no n8n:

Ajuste o URL nos nós "Processar Texto Ata" , "Processar Texto Edital" e "Merge-docx" para refletir o novo endereço.

📂 Estrutura de Pastas

input_docs/ → Contém o modelo TemplateAta.docx, usado como papel timbrado.

arquivo-teste/ → Contém arquivos de exemplo para testes.

output_docs/ → Salva as atas geradas após o processamento.

Geração de Ata: O texto processado é inserido no modelo TemplateAta.docx, gerando um novo documento.

