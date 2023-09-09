FROM python:3.11 as requirements-stage

ENV PYTHONUNBUFFERED 1

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11
WORKDIR /src
ENV PYTHONPATH /
COPY --from=requirements-stage /tmp/requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./src/ /src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
