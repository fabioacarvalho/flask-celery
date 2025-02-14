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
