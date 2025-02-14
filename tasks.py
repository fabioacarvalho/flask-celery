from celery_worker import celery

@celery.task(name="tasks.processar_tarefa")  # Nome explícito para evitar "__main__"
def processar_tarefa(x, y):
    return x + y
