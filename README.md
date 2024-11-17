# Code with Proofs: The Arena

[Demo Site](http://www.codeproofarena.com:8000/)

Main essay: [A Proposal for Safe and Hallucination-free Coding AI](https://gasstationmanager.github.io/ai/2024/11/04/a-proposal.html)

This repo implements a website with functionalities similar to online coding challenge sites like LeetCode, HackerRank and CodeForces, where users can submit solutions to coding challenges and be judged on test cases; except here the problems have function signatures with formal theorem statements, users submit code with proofs, and will be judged by the proof checker. Right now the only supported language is Lean, but I hope someone can extend it to other similar languages such as Coq, Idris, Dafny.

The purpose of this website is to serve as a platform to crowdsource efforts to create data on code-with-proof problems and solutions, including problem-only data as well as problem-with-solution data, both human-created and machine-created. And as a platform to share this data with the open-source community, for the purpose of training open-source models.

The web app is implemented in Python with the FastAPI library. Both web interface and API endpoints are available to create/manage challenges
and create/manage submissions. Automatic API documentation available; once the app is running
they are served  at `/docs` (Swagger UI), and  at `/redoc` (Redoc).

`scripts/import_challenges.py` is a simple script that creates challenges by importing from a JSONL file
in the format of [Code with Proofs Benchmark](https://github.com/GasStationManager/CodeProofBenchmark).

# Installation 

## Prerequisites

1. Python 3.10 or higher
2. PostgreSQL. E.g. on Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```
3. Poetry (Python package manager).
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
4. Lean 4.
```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
```

## Installation Instructions

1. clone the repository. `cd` into the directory. Then `poetry install` to install dependencies
2. Install Mathlib4. 
```bash
curl https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain -o lean-toolchain
lake exe cache get
```
3. Create a database and user in PostgreSQL. First, log into the server using `psql` as the superuser of the PosgresSQL installation. For Ubuntu:
`sudo -u postgres psql`. For Mac homebrew installation the user `postgres` is not installed; you might try
`psql` with the current user, as suggested by [this StackOverflow](https://stackoverflow.com/questions/70487669/postgres-superuser-is-not-created-upon-installation).


4. In PostgreSQL prompt (replace with your password):

```
CREATE DATABASE coding_challenge_db;
CREATE USER coding_challenge_user WITH PASSWORD 'your_password_here';

GRANT CONNECT ON DATABASE coding_challenge_db TO coding_challenge_user;

\c coding_challenge_db

GRANT USAGE, CREATE ON SCHEMA public TO coding_challenge_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO coding_challenge_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO coding_challenge_user;

\q
```

5. Then set up connection to PostgreSQL in `app/core/config.py` and in `alembic.ini` (around line 64) by filling in the password you chose.

6. `poetry run alembic upgrade head` 

7. `./run.sh`
