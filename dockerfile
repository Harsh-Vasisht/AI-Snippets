# Use a slim Python image for a smaller footprint
FROM python:3.10-slim

# Set an author label
LABEL authors="harshvasisht"

# Set the working directory inside the container
# All subsequent commands will run from here
WORKDIR /app

COPY pull_request_agent/src/requirements.txt requirements.txt

# The secret is mounted here specifically for pip install from a private repo
# We now copy the entire project and install requirements from the correct location
RUN --mount=type=secret,id=gcp_creds,target=/tmp/gcp_key.json,mode=0444 \
    pip install keyring keyrings.google-artifactregistry-auth && \
    export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_key.json && \
    pip install --index-url https://us-central1-python.pkg.dev/alan-suite/llm-studio-pypi/simple \
                --extra-index-url https://pypi.org/simple/ \
                -r requirements.txt


# Copy the requirements file and install dependencies
# We copy the entire project first to avoid issues with inconsistent COPY commands
# Copy only the .env which is present in the pull_request_agent/src in the root, so that when we run.py the llm studio will be able to access .env
COPY . .
# uncomment below line when running locally
# COPY pull_request_agent/src/.env .env 
# COPY pull_request_agent/src/run.py run.py


# NOTE: The GOOGLE_APPLICATION_CREDENTIALS export above is only for this RUN command.
# The secret file at /tmp/gcp_key.json is NOT included in the final image.

# Ensure that Python output is not buffered so you see logs immediately
ENV PYTHONUNBUFFERED=1

# Expose the port your application listens on
EXPOSE 5002

# The corrected command to run your application.
# The "-m" flag tells Python to run the file as a module.
# The path is relative to the directory containing the package, which is /app.
CMD ["python", "run.py"]
# CMD ["python", "-m", "pull_request_agent.src.run"]



# docker build -t pr_agent -f pull_request_agent/src/Dockerfile --secret id=gcp_creds,src=pull_request_agent/src/credentials.json .

# docker run -p 5002:5002 -v pull_request_agent/src/credentials.json -e GOOGLE_APPLICATION_CREDENTIALS=credentials.json pr_agent:latest
