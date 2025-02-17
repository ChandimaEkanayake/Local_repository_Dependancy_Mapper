import ast
import os
import pathlib
from collections import defaultdict
from core.ast_parser.ast_utils import get_dotted_name, get_module_name, get_py_files, method_decorator, module_name_to_path
from core.graph_database.database_handler import GraphDatabaseHandler


class AstManager:

    def __init__(self, project_path: str, task_id: str, graphDB: GraphDatabaseHandler):
        self.project_path = project_path
        self.root_path = project_path
        self.graphDB = graphDB
        self.task_id = task_id
        self.class_inherited = {}
        self.processed_relations = set()
        self.visited = []

    @method_decorator
    def run(self, py_files=None):
        if py_files is None:
            py_files = get_py_files(self.project_path)
        for py_file in py_files:
            self.build_modules_contain(py_file)
        for py_file in py_files:
            self.build_inherited(py_file)
        for cur_class_full_name in self.class_inherited.keys():
            for base_class_full_name in self.class_inherited[cur_class_full_name]:
                self._build_inherited_method(cur_class_full_name, base_class_full_name)

    def build_modules_contain(self, file_full_path):
        if file_full_path in self.visited:
            return None
        self.visited.append(file_full_path)
        try:
            file_content = pathlib.Path(file_full_path).read_text()
            tree = ast.parse(file_content)
        except Exception:
            return None
        if '__init__.py' in file_full_path:
            cur_module_full_name = get_dotted_name(self.root_path, os.path.dirname(file_full_path))
        else:
            cur_module_full_name = get_dotted_name(self.root_path, file_full_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                target_module_full_name = get_module_name(file_full_path, node, self.root_path)
                if target_module_full_name:
                    for target in node.names:
                        self._build_modules_contain_edge(target_module_full_name, target.name, cur_module_full_name)

    def build_inherited(self, file_full_path):
        try:
            file_content = pathlib.Path(file_full_path).read_text()
            tree = ast.parse(file_content)
        except Exception:
            return None
        if '__init__.py' in file_full_path:
            cur_module_full_name = get_dotted_name(self.root_path, os.path.dirname(file_full_path))
        else:
            cur_module_full_name = get_dotted_name(self.root_path, file_full_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                cur_class_full_name = cur_module_full_name + '.' + class_name
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_class_full_name, _ = self.get_full_name_from_graph(cur_module_full_name, base.id)
                        if base_class_full_name:
                            self.class_inherited.setdefault(cur_class_full_name, []).append(base_class_full_name)
                            self.graphDB.update_edge(start_name=cur_class_full_name, relationship_type='INHERITS', end_name=base_class_full_name)

    def _build_inherited_method(self, cur_class_full_name, base_class_full_name):
        relation_key = (cur_class_full_name, base_class_full_name)
        if relation_key in self.processed_relations:
            return
        self.processed_relations.add(relation_key)
        methods = self.get_all_edge_of_class(base_class_full_name)
        if methods:
            for node_full_name, name, relationship_type in methods:
                if not self.check_exist_edge_of_class(cur_class_full_name, name):
                    self.graphDB.update_edge(start_name=cur_class_full_name, relationship_type=relationship_type, end_name=node_full_name)
            if base_class_full_name in self.class_inherited:
                for base_base_class_full_name in self.class_inherited[base_class_full_name]:
                    self._build_inherited_method(cur_class_full_name, base_base_class_full_name)

    def get_full_name_from_graph(self, module_full_name, target_name):
        query = f"MATCH (m:MODULE:`{self.task_id}` {{full_name: '{module_full_name}'}})-[:CONTAINS]->(c:`{self.task_id}` {{name: '{target_name}'}}) RETURN c.full_name, labels(c)"
        result = self.graphDB.execute_query(query)
        if result:
            return result[0]['c.full_name'], result[0]['labels']
        return None, None

    def get_all_name_from_graph(self, module_full_name):
        query = f"MATCH (m:MODULE:`{self.task_id}` {{full_name: '{module_full_name}'}})-[:CONTAINS]->(c) RETURN c.full_name, labels(c)"
        result = self.graphDB.execute_query(query)
        return [(record['c.full_name'], record['labels']) for record in result] if result else []

    def get_all_edge_of_class(self, class_full_name):
        query = f"MATCH (c:CLASS:`{self.task_id}` {{full_name: '{class_full_name}'}})-[r]->(m) RETURN m.full_name, m.name, type(r)"
        result = self.graphDB.execute_query(query)
        return [(record['m.full_name'], record['m.name'], record['type(r)']) for record in result] if result else []

    def check_exist_edge_of_class(self, class_full_name, node_name):
        query = f"MATCH (c:CLASS:`{self.task_id}` {{full_name: '{class_full_name}'}})-[r]->(m {{name: '{node_name}'}}) RETURN m.full_name"
        result = self.graphDB.execute_query(query)
        return bool(result)
