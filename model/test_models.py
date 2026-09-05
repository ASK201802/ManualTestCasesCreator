from typing import List, Literal, Optional, TypedDict
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str = Field(description="Unique Test Case ID, e.g., TC_REBAL_001")
    category: str = Field(
        description="Category e.g., Core Functional, Boundary, Math Integrity"
    )
    title: str = Field(description="Short descriptive test case title")
    preconditions: str = Field(description="Prerequisites before executing the test")
    steps: str = Field(description="Numbered step-by-step execution instructions")
    expected_result: str = Field(description="Expected outcome and validation criteria")
    priority: Literal["High", "Medium", "Low"] = Field(
        description="Priority: High, Medium, or Low"
    )
    tags: List[str] = Field(default=[], description="List of tags for the test case")


class TestSuite(BaseModel):
    test_cases: List[TestCase] = Field(description="List of test cases")


class QATestState(TypedDict):
    query: str = Field(description="The original query or request")
    retrieved_context: str = Field(
        description="The retrieved context from the knowledge base"
    )
    generated_test_cases: List[dict] = Field(description="The generated test suite")
    human_feedback: Optional[str] = Field(
        default=None, description="Feedback from the human reviewer"
    )
    approved: bool = Field(description="Whether the test suite has been approved")
