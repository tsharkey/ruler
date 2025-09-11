#!/bin/bash
# start the database
docker-compose up -d

# wait for the database to start
while ! docker-compose exec postgres pg_isready -U postgres -d postgres; do
  echo "Waiting for database to start..."
  sleep 1
done

# Connect via TCP to the exposed port
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d postgres -f build/schema.sql

echo "Database initialized"

echo "Seeding database..."
uv run script/seed.py --game-version 10 warhammer-10e-core-rules.json warhammer40k

echo "Creating embeddings..."
uv run script/create-embeddings.py

echo "Finished!"
