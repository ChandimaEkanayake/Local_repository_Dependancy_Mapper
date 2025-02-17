import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.ast_parser.ast_manager import AstManager
from core.graph_database.database_handler import GraphDatabaseHandler

def get_python_files(directory):
    """Retrieve all Python files from the specified directory."""
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def build_graph_database(repo_path, graph_db, task_id):
    """Build the graph database by processing Python files in parallel."""
    file_list = get_python_files(repo_path)
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file, repo_path, graph_db, task_id): file for file in file_list}

        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file {file}: {e}")

    end_time = time.time()
    print(f"Graph database built in {end_time - start_time:.2f} seconds")

def process_file(file_path, repo_path, graph_db, task_id):
    """Process an individual file to parse its AST and update the graph database."""
    ast_manager = AstManager(project_path=repo_path, task_id=task_id, graphDB=graph_db)
    ast_manager.build_modules_contain(file_path)
    ast_manager.build_inherited(file_path)