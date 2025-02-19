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
from flask import Flask, jsonify
from celery.result import AsyncResult
from celery import Celery

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

import tasks

@app.route('/executar')
def executar():
    from tasks import processar_tarefa
    task = processar_tarefa.delay(10, 20)  # Executa a tarefa em background
    return jsonify({"message": "Tarefa iniciada", "task_id": task.id}), 202

@app.route('/status/<task_id>')
def status(task_id):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == "SUCCESS":
        return jsonify({"task_id": task_id, "status": "COMPLETED", "result": task_result.result}), 200
    elif task_result.state == "PENDING":
        return jsonify({"task_id": task_id, "status": "PENDING"}), 202
    elif task_result.state == "FAILURE":
        return jsonify({"task_id": task_id, "status": "FAILED"}), 500
    else:
        return jsonify({"task_id": task_id, "status": task_result.state}), 200

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
Agora, inicie os serviços para aplicar as mudanças:

```sh
docker-compose up --build
```

---

### 📌 7. **Rotas**
Agora, você pode acessar as seguintes rotas:

- localhost:5000/executar : está rota vai gerar uma tarefa ID
- localhost:5000/status/<task_id> : está rota vai exibir o status da tarefa.

---

### 📌 7. **Retornos API**
Os retornos serão no seguinte formato:

- Iniciando uma nova tarefa:
```json
{
  "message": "Tarefa iniciada",
  "task_id": "1d3dbbac-9096-44a4-9d74-a59276d0e928"
}
```

- Tarefa pendente ou em execução:
```json
{
  "status": "PENDING",
  "task_id": "1f61ff70-eaa0-407b-89f2-1b9e71961935"
}
```

- Tarefa concluida:

```json
{
  "result": 30,
  "status": "COMPLETED",
  "task_id": "1d3dbbac-9096-44a4-9d74-a59276d0e928"
}
```

---

### 🚀 **Conclusão**  
Agora você tem um ambiente Flask + Celery rodando em Docker Compose. O **Flask** recebe as requisições, o **Celery** processa tarefas assíncronas e o **Redis** gerencia a fila.  
