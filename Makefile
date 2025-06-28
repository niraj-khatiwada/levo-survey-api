server.dev:
	uv run flask run --debug

db.migrate:
	uv run flask db migrate

db.migrate.upgrade:
	uv run flask db upgrade

db.migrate.downgrade:
	uv run flask db downgrade
