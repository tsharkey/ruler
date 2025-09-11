# Ruler

Just some examples/experiments for creating embeddigins for 40k rules

## Parsing the PDF

Gave the pdf to Llamaindex and let it parse it. Could probably tune this better. I only did this once just to get an example

Seems like you could probably get this to work better but right I am just storing the page text but you could potentially parse it smarter with headings and such

## Usage

### Requirements

#### Install UV
```
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

#### Install Docker
https://docs.docker.com/get-docker/
```

### Run

```
# runs the db, initial schema, seeding, and embedding creation
$ make init

# if you already have the db initialized
$ make start-db

# runs the server
$ make start-server

# run a query
$ curl -X POST -H "Content-Type: application/json" -d '{"question": "how does combat work", "limit": 5}' http://localhost:8000/query
```
