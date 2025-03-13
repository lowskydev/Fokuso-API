FROM python:3.9-alpine3.13
LABEL maintainer="lowsky"

# Tells Python to run in unbuffered mode which is 
# recommended when running Python within Docker containers
# (See the logs on the screen as we run it)
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-dev.txt /tmp/requirements-dev.txt
COPY ./app ./app 
# Tell the image where commands are run from
WORKDIR /app 
EXPOSE 8000

# if DEV flag is active docker-compose will overwrite this (to true)
ARG DEV=false

# 1 - create py virtual environment so you don't have conflicing dependencies
# 2 - upgrade pip
# 3 - install requirements
# 4 - if DEV flag is active install dev requirements
# 5 - remove the temporary directory to keep the image small
# 6 - create a user to run the application (because... best practice - do NOT use root user)
#   1. no password
#   2. no home directory - not neccesary and we want to keep the image small
#   3. user name
RUN python -m venv /py && \ 
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \ 
        then /py/bin/pip install -r /tmp/requirements-dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Add our virtual environment to the path (so we don't need to specify whole path)
ENV PATH="/py/bin:$PATH"

# Switch to the user we created (run at the end so other is run by root user)
USER django-user