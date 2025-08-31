# URL Shortener Project

This is a simple URL shortener service built with Flask and SQLite. It provides a web interface and API to shorten URLs and redirect to the original URLs.

## Prerequisites

- Docker
- Docker Compose

## Docker Configuration

### Dockerfile Explanation

The `Dockerfile` defines the container image for the URL shortener service:

- `FROM python:3.11-slim`: Uses a lightweight Python 3.11 base image
- `WORKDIR /app`: Sets the working directory inside the container to `/app`
- `RUN apt-get update`: Updates the package list (required for some dependencies)
- `COPY . .`: Copies all files from the host to the container's working directory
- `RUN pip install --no-cache-dir -r requirements.txt`: Installs Python dependencies without caching to reduce image size
- `EXPOSE 5000`: Exposes port 5000 for the Flask application
- `CMD ["python3", "app.py"]`: Runs the Flask application when the container starts

### Docker Compose Configuration

The `docker-compose.yml` file orchestrates the service:

- `version: "3.8"`: Specifies the Docker Compose file format version
- `services`: Defines the services to run
  - `url-shortener`: The name of the service
    - `build: .`: Builds the Docker image from the current directory (using the Dockerfile)
    - `ports: - "5000:5000"`: Maps port 5000 on the host to port 5000 in the container

## Running with Docker Compose

1. Build and start the service:

```bash
docker-compose up --build
```

2. The service will be available at: [http://localhost:5000](http://localhost:5000)

3. The SQLite database is persisted in the `./data` directory on the host.

## API Usage

### Shorten a URL

```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com"}'
```

Response:

```json
{
  "short_code": "abc123",
  "short_url": "http://localhost:5000/abc123",
  "long_url": "https://www.example.com"
}
```

### Redirect to Original URL

Visit the shortened URL in your browser or use curl:

```bash
curl -I http://localhost:5000/abc123
```

### Health Check

```bash
curl http://localhost:5000/health
```

### Stats

```bash
curl http://localhost:5000/stats
```

### List Recent URLs

```bash
curl http://localhost:5000/list
```

## Notes

- The app source code is mounted into the container for easy development.
- The database file is stored in `./data/urls.db` on the host and `/app/data/urls.db` inside the container.
- The Flask environment is set to development in the docker-compose file.

## Stopping the Service

To stop the service, press `Ctrl+C` in the terminal running docker-compose, or run:

```bash
docker-compose down
```


