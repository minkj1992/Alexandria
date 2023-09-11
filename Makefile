up:
	@docker compose up --build -d --remove-orphans

logs:
	@docker compose logs -f

down:
	@docker compose down

.PHONY: test
test: up test-categorizer test-chat test-summarizer

test-categorizer:
	cd services/categorizer && make test

test-chat:
	cd services/chat && make test

test-summarizer:
	cd services/summarizer && make test
