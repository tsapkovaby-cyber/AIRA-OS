import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


class KnowledgeGraphArchitectureTests(unittest.TestCase):
    def test_node_example_matches_required_schema_contract(self):
        schema = load_json("schemas/knowledge_graph/node.schema.json")
        example = load_json("examples/knowledge_graph/node.example.json")
        self.assertTrue(set(schema["required"]).issubset(example.keys()))
        self.assertIn(example["category"], schema["properties"]["category"]["enum"])
        self.assertGreaterEqual(example["layer"], schema["properties"]["layer"]["minimum"])
        self.assertLessEqual(example["layer"], schema["properties"]["layer"]["maximum"])
        self.assertIn(example["visibility"], schema["properties"]["visibility"]["enum"])
        self.assertGreaterEqual(example["confidence"], 0)
        self.assertLessEqual(example["confidence"], 1)

    def test_relationship_example_matches_required_schema_contract(self):
        schema = load_json("schemas/knowledge_graph/relationship.schema.json")
        example = load_json("examples/knowledge_graph/relationship.example.json")
        self.assertTrue(set(schema["required"]).issubset(example.keys()))
        self.assertIn(example["type"], schema["properties"]["type"]["enum"])
        self.assertIn(example["visibility"], schema["properties"]["visibility"]["enum"])
        self.assertGreaterEqual(example["strength"], 0)
        self.assertLessEqual(example["strength"], 1)
        self.assertGreaterEqual(example["confidence"], 0)
        self.assertLessEqual(example["confidence"], 1)

    def test_relationship_requires_distinct_nodes(self):
        relationship = load_json("examples/knowledge_graph/relationship.example.json")
        self.assertNotEqual(relationship["sourceNodeId"], relationship["targetNodeId"])

    def test_node_scores_are_complete(self):
        node = load_json("examples/knowledge_graph/node.example.json")
        expected_scores = {
            "confidence",
            "importance",
            "freshness",
            "popularity",
            "businessValue",
            "educationalValue",
            "completeness",
        }
        self.assertEqual(expected_scores, set(node["scores"].keys()))
        for score in node["scores"].values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)


if __name__ == "__main__":
    unittest.main()
