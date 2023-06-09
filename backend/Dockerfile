FROM --platform=linux/arm64 python:3.11 as stage-arm64
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"

FROM --platform=linux/386 python:3.11 as stage-386
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

ARG TARGETARCH

FROM stage-$TARGETARCH as final
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws --version
RUN pip install pipenv
WORKDIR /app
ADD Pipfile.lock .
RUN pipenv install --ignore-pipfile
ADD Pipfile .
ADD lib lib
ADD main.py .
ENTRYPOINT ["pipenv", "run", "main", "all", "--all-sources"]