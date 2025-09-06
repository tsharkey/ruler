# Ruler

Just some examples/experiments for creating embeddigins for 40k rules

## Parsing the PDF

Gave the pdf to Llamaindex and let it parse it. Could probably tune this better. I only did this once just to get an example

Seems like you could probably get this to work better but right I am just storing the page text but you could potentially parse it smarter with headings and such

## Usage
```
# honestly not sure how this works with python but create the vent and install requirements
$ make venv

# runs the db, initial schema, seeding, and embedding creation
$ make init

# does vector search
$ python3 search.py "how does combat work" 5
```
