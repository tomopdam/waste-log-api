# waste-log-api
Example RESTful API for a waste logging management service.

## Run the service

0. Copy `.env.example` to `.env`.
1. Run `docker compose up` to get the containers set up.
2. In another terminal, run `docker compose exec api_dev python /waste-api/app/setup_service.py` to seed the database with an admin, teams, managers, employees, etc.
3. Open `http://localhost:80/docs` in your browser to access the api documentation. 
4. Login with default admin account via the top-right `Authorize`. Username is `admin` and password is `admin`.
5. Seed account login credentials are available at `/app/setup_service.py`. Manager passwords will be `manager` and employee passwords will be `employee`.

## Architecture

1. Docker containers for dev environment: nginx + fastapi/sqlmodel/pydantic + postgres
2. Separate docker containers for pytest setup and test database
3. Placeholder setup for a production build of the fastapi container

## Features

1. Users: Admin, Manager, Employee roles and applied permission checks via dependency injection
2. Models and schema: Users, Teams, Waste Logs, Analytics via SQLModel, pydantic, and alembic
3. JWT Authorization and admin-only forced token invalidation
4. Isolated docker test environment and database with mounted volume for the coverage report output
5. Foundation for custom exception handling and logging
6. Custom exception handling for common database exceptions
7. Basic setup for host-machine linting via poetry, with black, flake8, isort

## Schema:

- Models are via SQLModel: User, Team, WasteLog with associated schema for CRUD operations
- Some models include basic functional relationship metadata
- Some models include automatic datetime fields, created_at and updated_at
- Combinatory usage of team id and user role allow fluid permission checks for employees and managers

## Linting

1. Install poetry and add it to the system-wide environment variables.
2. In the root folder (where you see `pyproject.toml`), run `poetry install`.
3. Run: `poetry run black .`, `poetry run isort .`, `poetry run flake8 .`.

## Running tests

Run: `docker compose -f docker-compose.tests.yml up --abort-on-container-exit`.

Tests output will be in the terminal and in `tests/htmlcov/`.

## Further development notes / tech debt

1. Scale by splitting into separate microservices: 1) write waste log, and 2) management/analytics
2. Scale by replicating postgres databases into WRITE -> READ + READ + READ (and so on)
3. All database operations should be separated from route logic
4. Refactor permissions implementation
5. Finish applying recommendations from `poetry run flake8 .`
6. Improved docstring coverage, comments, and so forth