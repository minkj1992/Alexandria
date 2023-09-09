up:
	@docker compose up --build -d --remove-orphans
	@docker compose logs -f

down:
	@docker compose down
