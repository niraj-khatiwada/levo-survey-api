server.dev:
	uv run flask run --debug

db.migrate:
	uv run flask db migrate

db.migrate.upgrade:
	uv run flask db upgrade

db.migrate.downgrade:
	uv run flask db downgrade

docker.dev.up:
	docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.dev.yml up -d
	
docker.dev.down:
	docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.dev.yml down


docker.prod.up:
	docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.prod.yml up -d --build --force-recreate
	
docker.prod.down:
	docker compose --env-file .env --env-file .env.docker -f ./docker-compose.yml -f ./docker-compose.prod.yml down
