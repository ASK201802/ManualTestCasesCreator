from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from rag_parser.generator import generate_test_cases
from rag_parser.vctore_store_setter import retrieve_context
from model.test_models import QATestState
from util.exporter import export_to_json


def retrieve_node(state: QATestState) -> dict[str, Any]:
    context = retrieve_context(state["query"])
    return {"retrieved_context": context}


def generate_node(state: QATestState) -> dict[str, Any]:
    generated = generate_test_cases(state)
    return {"generated_test_cases": generated}


def human_review_node(state: QATestState) -> dict[str, Any]:
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
    """Node 4: Writes test cases to Excel if approved by the human reviewer."""
    print("[Node 4: Export] Checking approval status...")

    if state.get("approved"):
        export_to_json(state["generated_test_cases"])
    else:
        print(" -> Skipping Excel creation because the test suite was rejected.")

    return {}


def create_graph():
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

