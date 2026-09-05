import json

JSON_OUTPUT_PATH = "Approved_Rebalancing_Test_Cases.json"


def export_to_json(test_cases: list, filename: str = JSON_OUTPUT_PATH):
    """Writes approved manual test cases to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    print(f"\n[Exporter] Successfully exported {len(test_cases)} test cases to '{filename}'!")