from py2neo import Graph, Node, NodeMatcher, Relationship, RelationshipMatcher
import fasteners

class GraphDatabaseHandler:

    def __init__(self, uri, user, password, database_name='neo4j'):
        self.graph = Graph(uri, auth=(user, password), name=database_name)
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)

    def add_node(self, label, name, properties):
        node = self.node_matcher.match(label, name=name).first()
        if not node:
            node = Node(label, name=name, **properties)
            self.graph.create(node)
        return node

    def add_relationship(self, start_node_name, start_label, end_node_name, end_label, relationship_type, properties=None):
        start_node = self.node_matcher.match(start_label, name=start_node_name).first()
        end_node = self.node_matcher.match(end_label, name=end_node_name).first()
        if start_node and end_node:
            rel = Relationship(start_node, relationship_type, end_node, **(properties or {}))
            self.graph.create(rel)

    def clear_database(self):
        self.graph.run("MATCH (n) DETACH DELETE n")

    def execute_query(self, query, **params):
        try:
            return list(self.graph.run(query, **params))
        except Exception as e:
            print(f"Query failed: {e}")
            return []
