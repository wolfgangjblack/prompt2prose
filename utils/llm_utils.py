import os

from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))


def chat_with_gpt(
    messages,
    max_tokens=400,
    temperature=0.3,
    input_cost=0.5 / 1e6,
    output_cost=1.5 / 1e6,
):
    """Calls the OpenAI Chat Completion API with the provided messages."""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    cost = (
        completion.usage.prompt_tokens * input_cost
        + completion.usage.completion_tokens * output_cost
    )
    return completion.choices[0].message.content.strip(), cost
