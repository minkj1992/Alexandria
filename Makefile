up:
	@docker compose up --build -d --remove-orphans
	@docker compose logs -f

down: 
	@docker compose down

test-up:
	@docker compose --file docker-compose.test.yml up --build -d --remove-orphans
	make test-log

test-unit:
	cd chat && make test

test-log:
	@docker compose --file docker-compose.test.yml logs -f

test-build:
	@docker compose --file docker-compose.test.yml build --no-cache

test-down:
	@docker compose --file docker-compose.test.yml down

init:
	cp chat/env.example chat/.env

init-test:
	cp chat/env.test.example chat/.env.test