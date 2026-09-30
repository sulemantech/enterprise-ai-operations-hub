import sys
from typing import TypedDict
import anthropic
from ask import call_model, execute_tool
from langgraph.graph import StateGraph, START, END


class ReadinessState(TypedDict):
    messages: list[dict]
    needs_tool: bool
    answer:str


def request_assessment(state: ReadinessState) -> ReadinessState:
    response = call_model(
        client = anthropic.Anthropic(),
        messages = state["messages"],
         system_prompt=(
            "You help users check contractor readiness. "
            "Use get_job_assessment for questions about a job's readiness. "
            "If the job ID is missing, ask for it. Never invent an assessment."
        ),
        tool_choice={"type": "auto"},
    )

    if response.stop_reason not in ("tool_use", "end_turn"):
        raise RuntimeError(
            f"Model request did not finish normally: {response.stop_reason}"
            )
    needs_tool = response.stop_reason == "tool_use"

    text = "\n".join(
        block.text for block in response.content
        if(block.type =="text")
    )
    return {
        "messages": state["messages"] + [
            {
                "role":"assistant",
                "content":[
                    block.model_dump(mode="json")
                    for block in response.content
                ],
            }
        ],
        "needs_tool": needs_tool,
        "answer":"" if needs_tool else text,
    }

def run_tools(state:ReadinessState)->ReadinessState:
    assistant_message = state["messages"][-1]
    tool_results = []
    for block in assistant_message["content"]:
        if block["type"]=="tool_use":
            outcome = execute_tool(block["name"], block["input"])
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block["id"],
                **outcome,
            })
    if not tool_results:
        raise ValueError(f"Tool execution requires a tool request")
    return {
        "messages": state["messages"] + [
            {"role": "user", "content": tool_results}
        ],
        "needs_tool": False,
        "answer": "",
    }

def explain_assessment(state:ReadinessState) -> ReadinessState:
    response = call_model(
        anthropic.Anthropic(),
        messages=state["messages"],
        tool_choice={"type":"none"},
         system_prompt=(
            "Explain the readiness assessment using only the tool results. "
            "Preserve the returned status and reason. "
            "If a tool reports an error, explain the problem without "
            "inventing a readiness status. "
            "Keep the explanation to 2-3 sentences."
        ),
        )
    if response.stop_reason != "end_turn":
        raise RuntimeError(
            f"Explanation did not finish normally: {response.stop_reason}"
        )
     
    text = "\n".join(
            block.text for block in response.content
            if(block.type =="text")
        )
    return {
        "messages": state["messages"] + [
            {
                "role": "assistant",
                "content": [
                    block.model_dump(mode="json")
                    for block in response.content
                ],
            }
        ],
        "needs_tool": False,
        "answer": text,
    }

def route_after_request(state:ReadinessState) -> str:
    if state["needs_tool"]:
        return "run_tools"
    return "finish"


def build_graph():
    builder = StateGraph(ReadinessState)
    builder.add_node("request_assessment", request_assessment)
    builder.add_node("run_tools", run_tools)
    builder.add_node("explain_assessment",explain_assessment)

    builder.add_edge(START, "request_assessment")
    builder.add_conditional_edges(
        "request_assessment",
        route_after_request,
        {
            "run_tools": "run_tools",
            "finish":END,
        },
    )
    builder.add_edge("run_tools","explain_assessment")
    builder.add_edge("explain_assessment", END)

    return builder.compile()


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Why is JOB-102 blocked?"

    initial_state = {
        "messages": [{"role": "user", "content": question}],
        "needs_tool": False,
        "answer": "",
    }

    graph = build_graph()
    result = graph.invoke(initial_state)
    print(result["answer"])