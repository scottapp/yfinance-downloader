# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim

# Install production dependencies.
#RUN pip install Flask gunicorn
RUN pip install --upgrade google-cloud-storage
RUN pip install --upgrade google-cloud-pubsub
RUN pip install pytest
RUN pip install yfinance

# Copy local code to the container image.
WORKDIR /app
RUN mkdir /app/log
COPY . .


# Service must listen to $PORT environment variable.
# This default value facilitates local development.
#ENV PORT 8080
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
#CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app
CMD python src/main_download_prices.py
