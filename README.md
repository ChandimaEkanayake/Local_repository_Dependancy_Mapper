# Local_repository_Dependancy_Mapper

This project parses Python repositories into an AST, analyzes dependencies, and stores relationships in Neo4j.

## Setup
```bash
bash scripts/setup_env.sh
```

## Usage
```bash
python apps/cli/run_mapper.py
```

## Testing
```bash
python -m unittest discover tests