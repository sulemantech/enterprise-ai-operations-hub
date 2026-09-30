import sys
import json
import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field
from assessment_service import get_job_assessment
from explain import MODEL
from ai_tools import ASSESS_JOB_TOOL

class AssessmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    job_id: str = Field(min_length=1)

def call_model(client, messages, system_prompt, tool_choice):
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        tools=[ASSESS_JOB_TOOL],
        tool_choice=tool_choice,
        messages=messages,
    )

def ask(question: str) -> None:
    client = anthropic.Anthropic()

    response = call_model(
        client=client,
        messages=[{"role": "user", "content": question}],
        system_prompt=(
            "You help users check contractor readiness. "
            "Use get_job_assessment for questions about a job's readiness. "
            "If the job ID is missing, ask for it. Never invent an assessment."
        ),
        tool_choice={"type": "auto"},
    )
    print("Stop reason:", response.stop_reason)
    tool_results = []
    
    for block in response.content:
        if block.type =="tool_use":
            print("Tool:", block.name)
            print("Arguments:", block.input)
            if block.name != "get_job_assessment":
                raise ValueError(f"Unknown tool:{block.name}")
            
            arguments = AssessmentInput.model_validate(block.input)
            try:
                result = get_job_assessment(arguments.job_id)
            
            except ValueError as error:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "is_error": True,
                    "content": str(error),
                })
            else:
                print("Assessment:", result["status"], result["reason"])

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        elif block.type =="text":
            print(block.text)

    if tool_results:
        answer = call_model(
            client=client,
            messages=[
                {"role": "user", "content": question},
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results},
            ],
            system_prompt=(
                "Explain the readiness assessment using only the tool results. "
                "Preserve the returned status and reason. "
                "Explain the relevant evidence in 2-3 plain sentences. "
                "Never invent facts or claim that any follow-up was performed."
            ),
            tool_choice={"type": "none"},
        )
        if answer.stop_reason != "end_turn":
            raise RuntimeError(
                f"Explanation did not finish normally: {answer.stop_reason}"
            )

        for block in answer.content:
            if block.type == "text":
                print("Answer:", block.text)

if __name__ == "__main__":
    ask(sys.argv[1] if len(sys.argv) > 1 else "Why is JOB-102 blocked?")
