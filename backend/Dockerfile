FROM --platform=linux/arm64 python:3.11 as stage-arm64
ARG cli_url="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"

FROM --platform=linux/amd64 python:3.11 as stage-amd64
ARG cli_url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"

ARG TARGETARCH

FROM stage-$TARGETARCH as final
RUN pip install pipenv
RUN curl $cli_url -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws --version
WORKDIR /app
ADD Pipfile.lock .
ADD Pipfile .
RUN pipenv install --deploy
ADD lib lib
ADD main.py .
ENTRYPOINT ["pipenv", "run", "main", "all", "--all-sources"]