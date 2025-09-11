.PHONY: init start clean seed connect venv

init:
	./script/init.sh

start:
	./script/start.sh

clean:
	docker compose down
	rm -rf postgres

seed:
	uv run seed.py --game-version 10 warhammer-10e-core-rules.json warhammer40k
	 
connect:
	PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d postgres
