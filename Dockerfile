FROM python:3.10

WORKDIR /code

COPY ./api /code/api/
COPY ./db /code/db/
COPY ./migrations /code/migrations/
COPY ./tasks /code/tasks/
COPY ./*.py /code/
COPY ./*.txt /code/
COPY ./alembic.ini /code/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


#
CMD ["alembic", "upgrade", "head"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
