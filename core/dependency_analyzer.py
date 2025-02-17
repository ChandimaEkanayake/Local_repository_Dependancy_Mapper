import ast

class DependencyAnalyzer:
    def __init__(self, graph_db):
        self.graph_db = graph_db

    def analyze_dependencies(self, code_snippet):
        tree = ast.parse(code_snippet)
        dependencies = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                dependencies.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name)

        return list(dependencies)