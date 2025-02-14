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
