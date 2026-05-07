FROM python:3.10

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY /tasks/*.py /code/tasks/
COPY ./db/models.py /code/db/
COPY settings.py /code/
COPY user_agent.txt /code/
CMD ["celery", "-A", "tasks.tasks", "worker", "-B", "--loglevel=INFO"]