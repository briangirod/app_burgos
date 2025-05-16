FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app/

EXPOSE 8000

RUN pip install --upgrade pip && pip install -r requirements.txt

# Si usás PostgreSQL puede ser necesario instalar dependencias:
# RUN apt-get update && apt-get install -y libpq-dev gcc

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
