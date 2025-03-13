# Django API with Docker for Studying Software

This is a Django-based API application containerized with Docker. The application includes API documentation using Swagger UI and employs GitHub Actions for linting and testing.

## Features

- Django API application
- Dockerized setup (for both database and app)
- Swagger UI for API documentation
- GitHub Actions for CI/CD (linting and testing)
- Admin panel for database management

## Getting Started

### Prerequisites

Ensure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Clone the repository

```bash
git clone https://github.com/yourusername/study-learning-web-app.git
```

### Running the Application

To start the service, run:

```sh
docker compose up
```

To stop the service:

```sh
docker compose down
```

### Accessing the Application

- **API Documentation**: [Swagger UI](http://127.0.0.1:8000/api/docs)
- **Admin Panel**: [Django Admin](http://127.0.0.1:8000/admin)

### Running Tests

To run tests directly in the app container:

```sh
docker compose run --rm app sh -c "python manage.py test"
```

### Creating a Superuser

To create a superuser for the admin panel:

```sh
docker compose run --rm app sh -c "python manage.py createsuperuser"
```

### Applying Migrations

Ensure database migrations are applied:

```sh
docker compose run --rm app sh -c "python manage.py migrate"
```

### Checking Code Formatting & Linting

If using `flake8` for linting, run:

```sh
docker compose run --rm app sh -c "flake8"
```

## Continuous Integration (CI)

This project uses GitHub Actions for automated testing and linting on every push and pull request.
