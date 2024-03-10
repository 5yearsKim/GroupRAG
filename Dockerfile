FROM python:3.10

WORKDIR /project
RUN pip install poetry

COPY poetry.lock pyproject.toml deploy.py config.py /project/
COPY group_ragger /project/group_ragger

RUN poetry install --no-root

EXPOSE 8010

CMD ["poetry", "run", "uvicorn", "deploy:app", "--host", "0.0.0.0", "--port", "8010"]






