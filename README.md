# URL Shortener Project

This is a simple URL shortener service built with Flask and SQLite. It provides a web interface and API to shorten URLs and redirect to the original URLs.

## Prerequisites

- Docker
- Docker Compose

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


