FROM python:3.8

RUN pip install 'poetry>=0.12'
RUN poetry config virtualenvs.create false

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./
RUN poetry install --extras sqlite --no-root

ENV PYTHONPATH .

ENTRYPOINT ["/usr/local/bin/poetry", "run", "uvicorn", "fx:app"]
CMD []

COPY fx ./fx
