FROM python:3.9-alpine3.13
LABEL maintainer="sudhanshu"

# Set environment variables
ENV PYTHONUNBUFFERED 1

# COPY requirements.txt /requirements.txt
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

# Set work directory
WORKDIR /app

# Expose port
EXPOSE 8000

# Install dependencies
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
    
ENV PATH="/py/bin:$PATH"

USER django-user

# Run the application
CMD ["python", "manage.py", "runserver"]
