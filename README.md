# Code with Proofs: The Arena

Main essay: [A Proposal for Safe and Hallucination-free Coding AI](https://gasstationmanager.github.io/ai/2024/11/04/a-proposal.html)

This repo implements a website with functionalities similar to online coding challenge sites like LeetCode, HackerRank and CodeForces, where users can submit solutions to coding challenges and be judged on test cases; except here the problems have function signatures with formal theorem statements, users submit code with proofs, and will be judged by the proof checker. Right now the only supported language is Lean, but I hope someone can extend it to other similar languages such as Coq, Idris, Dafny.

The purpose of this website is to serve as a platform to crowdsource efforts to create data on code-with-proof problems and solutions, including problem-only data as well as problem-with-solution data, both human-created and machine-created. And as a platform to share this data with the open-source community, for the purpose of training open-source models.

# Installation 

## Prerequisites

1. Python 3.10 or higher
2. PostgreSQL
3. Poetry (Python package manager)
4. Lean 4

## Brief Installation Instruction

1. clone the repository
2. poetry install to install dependencies
3. set up connection to PostgreSQL in app/core/config.py and in alembic.ini
4. poetry run alembic upgrade head 
5. poetry run python run.py
