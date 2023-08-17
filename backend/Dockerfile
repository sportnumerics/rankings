FROM --platform=linux/arm64 python:3.11 as stage-arm64

FROM --platform=linux/amd64 python:3.11 as stage-amd64

ARG TARGETARCH

FROM stage-$TARGETARCH as final
RUN pip install pipenv
WORKDIR /app
ADD Pipfile.lock .
ADD Pipfile .
RUN pipenv install --deploy
ADD lib lib
ADD main.py .
ENTRYPOINT ["pipenv", "run", "main", "all", "--all-sources"]