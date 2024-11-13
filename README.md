# Code with Proofs: The Arena

Main essay: [A Proposal for Safe and Hallucination-free Coding AI](https://gasstationmanager.github.io/ai/2024/11/04/a-proposal.html)

This repo implements a website with functionalities similar to online coding challenge sites like LeetCode, HackerRank and CodeForces, where users can submit solutions to coding challenges and be judged on test cases; except here the problems have function signatures with formal theorem statements, users submit code with proofs, and will be judged by the proof checker. Right now the only supported language is Lean, but I hope someone can extend it to other similar languages such as Coq, Idris, Dafny.

The purpose of this website is to serve as a platform to crowdsource efforts to create data on code-with-proof problems and solutions, including problem-only data as well as problem-with-solution data, both human-created and machine-created. And as a platform to share this data with the open-source community, for the purpose of training open-source models.

The web app is implemented in Python with the FastAPI library. Both web interface and API endpoints are available to create/manage challanges
and create/manage submissions.

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

## Brief Installation Instruction

1. clone the repository
2. `poetry install` to install dependencies
3. Create a database and user:
```bash
sudo -u postgres psql
```
In PostgreSQL prompt (replace with your password):
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
Then set up connection to PostgreSQL in `app/core/config.py` and in `alembic.ini` by filling in the password you chose.
4. `poetry run alembic upgrade head` 
5. `./run.sh`
