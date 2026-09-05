from dotenv import load_dotenv
from langgraph.types import Command
load_dotenv()
from flow.graph import create_graph
from rag_parser.vctore_store_setter import intialize_and_ingest_pinecode

def main():
    print("Hello from testcasecreator!")
    intialize_and_ingest_pinecode()
    graph = create_graph()
    config = {"configurable": {"thread_id": "qa_session_001"}}
    initial_input={
        "query": """Generate test cases for portfolio rebalancing.
        The Test should validate the following with additional edge cases,boundary value analysis etc:
        - Portfolio rebalancing should calculate the correct number of units to buy/sell
        - Portfolio rebalancing should ensure total valuation of asset is same
        - Portfolio rebalancing should validate all the companies name valid before allocation are still valid
        - Portfolio rebalancing should validate target percentages are matched with current after rebalancing
        - Portfolio rebalancing should validate the total investment amount is correct, i.e 100$
        - protfolio rebalancing should validate deviation percentage is  0 after rebalancing
        - protfolio rebalancing should validate the unit price remain unchanged
""",
        "retrieved_context": "",
        "generated_test_cases": [],
        "human_feedback": None,
        "approved": False
    }
    
    
    for chunk in graph.stream(initial_input, config=config):
        print(chunk)
    snapshots = graph.get_state(config=config)
    print("snapshots    :", snapshots)
    pending_interrupt = snapshots.tasks[0].interrupts[0]
    print("pending_interrupt:", pending_interrupt)
    draft_test_cases = pending_interrupt.value['draft_test_cases']
    print("draft_test_cases:", draft_test_cases)

    print(f"\n================ PAUSED FOR QA REVIEW ================")
    print(f"Generated {len(draft_test_cases)} test cases.\n")
    for i, tc in enumerate(draft_test_cases, 1):
        print(f"  {i}. [{tc['id']}] {tc['title']} (Priority: {tc['priority']})")

    print("\nOptions: [approve] / [edit] / [reject]")
    action = input("Your decision: ").strip().lower()

    if action == "edit":
        print("Enter the updated test cases as a JSON list, or modify individual fields.")
        import json
        raw = input("Paste updated test cases JSON: ")
        edited_cases = json.loads(raw)
        resume_command = Command(resume={"action": "edit", "test_cases": edited_cases})
    elif action == "reject":
        resume_command = Command(resume={"action": "reject"})
    else:
        resume_command = Command(resume={"action": "approve"})

    print(f"\nResuming graph with action: {action}")
    for chunk in graph.stream(resume_command, config=config):
        print("list of event keys:", list(chunk.keys()))


if __name__ == "__main__":
    main()
