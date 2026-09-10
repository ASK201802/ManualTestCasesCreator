from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from rag_parser.generator import generate_test_cases
from rag_parser.vctore_store_setter import retrieve_context
from model.test_models import QATestState
from util.exporter import export_to_json


def retrieve_node(state: QATestState) -> dict[str, Any]:
    """Node 1: Retrieves relevant context from the Pinecone vector store based on the user query.

    Args:
        state: Current graph state containing the user query.

    Returns:
        Dict with 'retrieved_context' key containing the matched requirement text.
    """
    context = retrieve_context(state["query"])
    return {"retrieved_context": context}


def generate_node(state: QATestState) -> dict[str, Any]:
    """Node 2: Generates structured test cases using the LLM based on the retrieved context.

    Args:
        state: Current graph state containing the query and retrieved context.

    Returns:
        Dict with 'generated_test_cases' key containing a list of test case dicts.
    """
    generated = generate_test_cases(state)
    return {"generated_test_cases": generated}


def human_review_node(state: QATestState) -> dict[str, Any]:
    """Node 3: Pauses the graph for human-in-the-loop review of generated test cases.

    Presents draft test cases to the user and waits for a resume command.
    Supports three actions:
        - 'approve': Accept test cases as-is.
        - 'edit': Accept with user-provided modifications.
        - 'reject': Reject the test suite entirely.

    Args:
        state: Current graph state containing generated test cases.

    Returns:
        Dict with 'approved' and 'human_feedback' keys, and optionally updated test cases.

    Raises:
        ValueError: If the resume action is not one of approve, edit, or reject.
    """
    human_review_response = interrupt(
        {
            "message": "Please review ,edit or approve the generated test cases",
            "draft_test_cases": state["generated_test_cases"],
        }
    )
    action = human_review_response["action"]
    if action == "approve":
        return {"approved": True, "human_feedback": "approved_without_modification"}
    elif action == "edit":
        return {
            "approved": True,
            "human_feedback": "approved_with_modification",
            "generated_test_cases": human_review_response["test_cases"],
        }
    elif action == "reject":
        return {"approved": False, "human_feedback": "rejected"}
    else:
        raise ValueError("Invalid action")


def export_node(state: QATestState) -> Dict[str, Any]:
    """Node 4: Exports approved test cases to a JSON file.

    Skips export if the test suite was rejected during human review.

    Args:
        state: Current graph state containing approval status and test cases.

    Returns:
        Empty dict (terminal node, no state updates).
    """
    print("[Node 4: Export] Checking approval status...")

    if state.get("approved"):
        export_to_json(state["generated_test_cases"])
    else:
        print(" -> Skipping Json creation because the test suite was rejected.")

    return {}


def create_graph():
    """Creates and compiles the LangGraph workflow for test case generation.

    Graph flow: retrieve -> generate -> human_review -> export -> END.
    Uses an in-memory checkpointer to support interrupt/resume for human review.

    Returns:
        CompiledGraph: The compiled LangGraph state machine ready for streaming.
    """
    graph = StateGraph(QATestState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("export", export_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "human_review")
    graph.add_edge("human_review", "export")
    graph.add_edge("export", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)
