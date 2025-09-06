.PHONY: init start

init:
	./script/init.sh

start:
	./script/start.sh

clean:
	docker compose down
	rm -rf postgres

seed:
	python3 seed.py --game-version 10 warhammer-10e-core-rules.json warhammer40k
	 
connect:
	PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d postgres

venv:
	python3 -m venv venv
	source venv/bin/activate
	pip3 install -r requirements.txt
