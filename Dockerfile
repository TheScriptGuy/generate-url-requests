# Use Alpine Linux as the base image
FROM alpine:latest

# Set maintainer label
LABEL maintainer="TheScriptGuy"

# Set environment variables to non-interactive (this prevents some prompts)
ENV PYTHONUNBUFFERED=1

# Set Environment variables for python script.
ENV NUM_CONNECTIONS=100
ENV NUM_WORKERS=10

# Install Python3 and pip
# Also install other dependencies such as gcc and musl-dev to ensure certain Python packages like 'requests' can be installed
RUN apk --no-cache add python3 py3-pip gcc musl-dev && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel

# Install requests library for Python
RUN pip3 install requests

# Copy the Python script into the container
COPY generate-url-requests.py /app/generate-url-requests.py

# Set work directory
WORKDIR /app

# Command to run the script
# You can override these values at runtime using the docker run command with the -e option
CMD ["sh", "-c", "python3 generate-url-requests.py $NUM_CONNECTIONS $NUM_WORKERS"]