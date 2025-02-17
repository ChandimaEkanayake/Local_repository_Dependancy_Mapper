import sys
import os
from core.graph_database.database_handler import GraphDatabaseHandler
from core.graph_database.database_builder import build_graph_database
from core.dependency_analyzer import DependencyAnalyzer
import json


def main():
    # Load settings
    with open('config/settings.json', 'r') as f:
        settings = json.load(f)

    repo_path = settings['repo_path']
    neo4j_config = settings['neo4j']

    # Initialize database connection
    graph_db = GraphDatabaseHandler(
        uri=neo4j_config['url'],
        user=neo4j_config['user'],
        password=neo4j_config['password'],
        database_name=neo4j_config['database_name']
    )

    # Build AST and populate graph database using database builder
    build_graph_database(repo_path, graph_db, task_id='python_repo')

    # Initialize dependency analyzer
    analyzer = DependencyAnalyzer(graph_db)

    # Accept multiline code snippet from CLI
    print("Enter your code snippet (end with an empty line):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    code_snippet = "\n".join(lines)

    # Analyze dependencies
    dependencies = analyzer.analyze_dependencies(code_snippet)
    print("Dependencies:", dependencies)


if __name__ == '__main__':
    main()
