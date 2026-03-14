# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git

RUN pip3 install -r requirements.txt

EXPOSE 8501

COPY streamlit_app/*.py .
COPY streamlit_app/.streamlit/secrets.toml ./.streamlit/secrets.toml

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
