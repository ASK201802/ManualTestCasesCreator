# import os, sys
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv

load_dotenv()
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from model.test_models import TestSuite, QATestState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
SYSTEM_MESSAGE = """You are a Lead QA Automation Engineer specializing in Financial and Portfolio Rebalancing Systems.
Your objective is to generate manual test cases based STRICTLY on the provided requirement context.

Retrieved Context:
{context}

Requirements:
1. Include functional, edge-case, math calculation, and negative scenario test cases.
2. Go BEYOND the explicitly listed requirements — think creatively about race conditions, concurrency, rounding errors, floating-point precision, empty/null inputs, unauthorized access, and system failure recovery scenarios.
3. For each listed requirement, generate at least one positive and one negative test case.
4. Structure output strictly according to these format instructions:
{format_instructions}
"""
HUMAN_MESSAGE = """Generate manual test cases focusing on: {query}
"""


def generate_test_cases(state: QATestState) -> QATestState:
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_MESSAGE), ("human", HUMAN_MESSAGE)]
    )
    parser = PydanticOutputParser(pydantic_object=TestSuite)
    print(state["retrieved_context"])
    formatted_promt = prompt.format_messages(
        context=state["retrieved_context"],
        format_instructions=parser.get_format_instructions(),
        query=state["query"],
    )
    result = llm.invoke(formatted_promt)
    parsed_suite: TestSuite = parser.parse(result.content)
    test_cases_dict = [test_case.model_dump() for test_case in parsed_suite.test_cases]
    return test_cases_dict


# if __name__ == "__main__":
#     state = QATestState(
#         query="""Generate test cases for portfolio rebalancing.
#         The Test should validate the following:
#         - Portfolio rebalancing should calculate the correct number of units to buy/sell
#         - Portfolio rebalancing should ensure total valuation of asset is same
#         - Portfolio rebalancing should validate all the companies name valid before allocation are still valid
#         - Portfolio rebalancing should validate target percentages are matched with current after rebalancing
#         - Portfolio rebalancing should validate the total investment amount is correct, i.e 100$
#         - protfolio rebalancing should validate deviation percentage is  0 after rebalancing
#         - protfolio rebalancing should validate the unit price remain unchanged

#         """,
#         retrieved_context="Context about portfolio rebalancing"
#     )
#     result = generate_test_cases(state)
#     print(result)
