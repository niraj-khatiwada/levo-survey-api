# Levo Survey API

[Link](https://lserver.nirajkhatiwada.dev/)

### 📁 Architecture Overview

**Key Architectural Components**:

1. Dependency Injection (DI)
   - **Framework**: flask-injector with injector library
   - **Configuration**: src/modules.py - binds all services and repositories
   - **Scope**: Singleton pattern for all services
   - **Benefits**: Loose coupling, testability, maintainability
2. Repository Pattern
   - **Base Class**: src/shared/base_repository.py
   - **Implementation**: Each domain has its own repository
   - **Purpose**: Abstracts data access logic from business logic
3. Service Layer
   - **Business Logic**: Encapsulated in service classes
   - **Dependencies**: Injected through constructor
   - **Responsibilities**: Orchestrating domain operations
4. API Layer
   - **Framework**: Flask with Flask-Smorest
   - **Versioning**: /api/v1/ structure
   - **Validation**: Marshmallow schemas
   - **Documentation**: Auto-generated API docs. You can view the Swagger docker [here](https://lserver.nirajkhatiwada.dev/docs/swagger-ui)
5. Database Layer
   - **ORM**: SQLAlchemy
   - **Migrations**: Flask-Migrate with Alembic
   - **Models**: Domain entities as SQLAlchemy models

##### Data Flow:

`HTTP Request` → `API Route` → `Schema Validation` → `Service` → `Repository` → `Database` → `Repository` → `Service` → `Schema Parsing` → `HTTP Response`

##### Stack:

- **Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API**: Flask-Smorest (REST API with auto Swagger docs
- **Validation**: Marshmallow schemas
- **DI**: Flask-Injector
- **Email**: Flask-Mail
- **Scheduling**: APScheduler
- **Migrations**: Alembic
- **uv**: Package manager

## Steps to run:

- Clone the repo first:

```
git clone git@github.com:niraj-khatiwada/levo-survey-api.git
```

- Install packages:

```
uv sync
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you have't installed it.

- Copy environment variables files:

```
cp ./.env.example ./.env
cp  ./.env.docker.example ./.env.docker
```

- Run Docker containers:

---

Development

```
docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.dev.yml up -d

or

make docker.dev.up

```

---

Production:

```
docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.prod.yml up -d --build --force-recreate

or

make docker.prod.up

```

---

- Next, run database migrations:

```
# Enter into container first:

docker exec -it levo-server sh

# Migrate the database:

uv run flask db upgrade

```

- Restart server container:
  After migration, we need to restart our server to make sure APScheduler migrates it's required configurations and tables into the database. This is just one time thing.

```
docker container restart levo-server
```

Your server is now ready and running on port 5000

### Mail:

A custom SMTP server [MailPit](https://mailpit.axllent.org/) was used since I couldn't find a free mail server. You'll receive all the emails [here](https://lmail.nirajkhatiwada.dev/).
