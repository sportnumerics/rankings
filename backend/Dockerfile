FROM --platform=linux/arm64 python:3.11 as stage-arm64
ARG cli_url="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"

FROM --platform=linux/amd64 python:3.11 as stage-amd64
ARG cli_url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"

ARG TARGETARCH

FROM stage-$TARGETARCH as final-builder
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/
RUN curl $cli_url -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws --version
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project
ADD lib lib
ADD main.py .
ENTRYPOINT ["uv", "run", "main.py", "all", "--all-sources"]