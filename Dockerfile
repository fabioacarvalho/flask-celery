# Usar a imagem oficial do Python
FROM python:3.9

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY . /app

# Instalar dependências
RUN pip install -r requirements.txt

# Expor a porta do Flask
EXPOSE 5000

# Comando para iniciar o app
CMD ["python", "celery_worker.py"]
