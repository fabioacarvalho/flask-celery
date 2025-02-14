# Utilizando Celery + Redis em uma aplicação Flask com Docker

Para rodar o Celery com Flask em um ambiente **Docker**, você precisará configurar os seguintes serviços:

1. **Flask App** - A aplicação principal.
2. **Celery Worker** - Responsável por processar as tarefas em segundo plano.
3. **Redis** ou **RabbitMQ** - Um broker para gerenciar a fila de tarefas.

Exemplo completo para configurar isso:

---

### 📌 1. **Instalar Dependências**  
No seu Flask, adicione os pacotes necessários ao seu `requirements.txt`:

```txt
flask
celery
redis
```

---

### 📌 2. **Criar o `Dockerfile` para o Flask App**  

Crie um arquivo `Dockerfile` na raiz do projeto:

```dockerfile
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
```

---

### 📌 3. **Criar um Arquivo `tasks.py`**
Crie um novo arquivo `tasks.py` e mova a função da tarefa para ele:

```python
from celery_worker import celery

@celery.task(name="tasks.processar_tarefa")  # Definir um nome explícito
def processar_tarefa(x, y):
    return x + y
```

---

### 📌 4. **Criar o arquivo `celery_worker.py`**
Modifique `celery_worker.py` para garantir que as tarefas sejam importadas corretamente:

```python
from celery import Celery
from flask import Flask

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# Criar app Flask
app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)

celery = make_celery(app)

# Importar tarefas corretamente
import tasks  

@app.route('/executar')
def executar():
    from tasks import processar_tarefa  # Importação no escopo correto
    task = processar_tarefa.delay(10, 20)  # Executa a tarefa em background
    return f'Tarefa iniciada: {task.id}', 202

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

---

### 📌 5. **Criar o `docker-compose.yml`**
Modifique seu `docker-compose.yml` para garantir que o worker inicie corretamente:

```yaml
version: '3.8'

services:
  flask:
    build: .
    container_name: flask_app
    ports:
      - "5000:5000"
    depends_on:
      - redis

  redis:
    image: redis:latest
    container_name: redis_broker
    ports:
      - "6379:6379"

  worker:
    build: .
    container_name: celery_worker
    command: celery -A celery_worker.celery worker --loglevel=info
    depends_on:
      - redis
```

---

### 📌 6. **Iniciar os Containers**
Agora, reinicie os serviços para aplicar as mudanças:

```sh
docker-compose up --build
```

---

### 🚀 **Conclusão**  
Agora você tem um ambiente Flask + Celery rodando em Docker Compose. O **Flask** recebe as requisições, o **Celery** processa tarefas assíncronas e o **Redis** gerencia a fila.  
