ARG BASE_IMAGE="debian:stable-slim"
ARG PORT="3000"

FROM ${BASE_IMAGE} AS base

ARG PORT

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

# Build
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

# FIXME: docker doesn't seem to support relabel=shared
# add: ,relabel=shared at the end if using podman
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []

# Run
EXPOSE ${PORT}/tcp

ENV PORT=${PORT}

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "src/main.py"]
