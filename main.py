from dotenv import load_dotenv
from langgraph.types import Command
load_dotenv()
from flow.graph import create_graph
from rag_parser.vctore_store_setter import intialize_and_ingest_pinecode
import json

def main():
    """Entry point for the test case generation workflow.

    Initializes Pinecone, builds the LangGraph workflow, streams execution
    through retrieve -> generate -> human_review -> export, and pauses for
    user approval before exporting the final test cases to JSON.
    """
    print("Starting Requirements Parsing")
    intialize_and_ingest_pinecode()
    graph = create_graph()
    config = {"configurable": {"thread_id": "qa_session_001"}}
    initial_input={
        "query": "Generate test cases for portfolio rebalancing.",
        "retrieved_context": "",
        "generated_test_cases": [],
        "human_feedback": None,
        "approved": False
    }
    
    
    for chunk in graph.stream(initial_input, config=config):
        print(chunk)
    snapshots = graph.get_state(config=config)
    #print("snapshots    :", snapshots)
    pending_interrupt = snapshots.tasks[0].interrupts[0]
    #print("pending_interrupt:", pending_interrupt)
    draft_test_cases = pending_interrupt.value['draft_test_cases']
    print(f"Generated {len(draft_test_cases)} test cases.\n")
    for i, tc in enumerate(draft_test_cases, 1):
        print(f"  {i}. [{tc['id']}] {tc['title']} (Priority: {tc['priority']})")
    print(f"\n================ Draft Test Cases ================")
    print("draft_test_cases:", json.dumps(draft_test_cases, indent=2))
    print(f"\n================ Draft Test Cases End ================")
    print(f"\n================ PAUSED FOR QA REVIEW ================")

    print("\nOptions: [approve] / [edit] / [reject]")
    action = input("Your decision: ").strip().lower()

    if action == "edit":
        print("Enter the updated test cases as a JSON list, or modify individual fields.")
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
