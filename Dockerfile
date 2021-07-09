ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}-alpine as base
RUN apk update && \
    apk add \
        --no-cache \
        --virtual \
            .build-deps \
            gcc musl-dev \
            postgresql-dev \
            libxml2-dev \
            libxslt-dev \
            libxslt-dev \
            postgresql-libs

FROM base as build
WORKDIR /wheels
COPY requirements/* ./
ARG ENV=production
RUN pip install -U pip \    
    && pip wheel -r ./${ENV}.txt

FROM base as final
ARG APP_DIR=/app
WORKDIR $APP_DIR
COPY --from=build /wheels /wheels
ARG ENV=production
RUN pip install -U pip \
       && pip install -r /wheels/${ENV}.txt \
                      -f /wheels \
       && rm -rf /wheels \
       && rm -rf /root/.cache/pip/* 
COPY . .
