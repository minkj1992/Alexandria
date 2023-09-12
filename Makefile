up:
	@docker compose up --build -d --remove-orphans
	@docker compose logs -f

down: 
	@docker compose down

.PHONY: test
test: up test-chat

test-chat:
	cd chat && make test
