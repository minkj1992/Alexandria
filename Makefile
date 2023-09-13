up:
	@docker compose up --build -d --remove-orphans
	@docker compose logs -f

down: 
	@docker compose down

test-unit: up
	cd chat && make test

test-load:
	@docker compose --file docker-compose.test.yml up --build -d --remove-orphans
	@docker compose --file docker-compose.test.yml logs -f
	
test-down:
	@docker compose --file docker-compose.test.yml down
	