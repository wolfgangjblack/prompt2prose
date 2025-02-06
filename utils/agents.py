import json
from utils.api_utils import chat_with_gpt

def context_agent(beat, previous_context=None):
    """
    Analyzes a beat and (optionally) compares it with the previous context.
    Returns a JSON-formatted summary of the scene, e.g.:
    {
        "location": "forest",
        "location_change": false,
        "characters": [
            {"name": "Alice", "character_location": "on stage", "status_change": false},
            {"name": "Bob", "character_location": "off stage", "status_change": false}
        ]
    }
    """
    system_message = (
        "You are ContextAgent. Your job is to extract key scene details from a story beat and compare it with the previous scene context (if provided). "
        "Focus on the following: \n"
        "1. Location: Identify the scene's location. If the new beat describes a location that is essentially the same as the previous context (e.g., the same forest or room), then set 'location_change' to false. Only mark it as true if the beat explicitly indicates a change (for example, 'they enter a cabin' when the previous context was a forest). If no location information is specified, maintain location from the previous beat\n"
        "2. Characters: List each character mentioned in the beat along with their role in the scene. For each character, output their 'character_location' (e.g., 'on stage' if present in the scene, or 'off stage' if only mentioned remotely) and 'status_change': mark false if their role is unchanged from the previous context, or true if the beat indicates a new presence or a different mode of engagement.\n"
        "Return your answer strictly as JSON with keys: 'location', 'location_change', and 'characters' (which is a list of objects with keys 'name', 'character_location', and 'status_change').\n"
        "If no previous context is provided, assume this is the first beat and set all _change flags to false."
    )
    
    # Build the user prompt. If previous_context exists, include it.
    if previous_context:
        user_prompt = (
            f"Previous Context (JSON):\n{previous_context}\n\n"
            f"New Beat:\n\"{beat}\"\n\n"
            "Compare the new beat to the previous context. If the new beat describes the same location, mark 'location_change' as false; "
            "if it indicates a different location, mark it as true and update the 'location'."
            "For each character mentioned, compare with previous context: if their 'character_location' remains the same, mark 'status_change' as false; "
            "if it changes or a new character is introduced, mark it as true. "
            "Return the updated scene context in valid JSON format."
        )
    else:
        user_prompt = (
            f"New Beat:\n\"{beat}\"\n\n"
            "Extract the scene context. Identify the location and any characters along with their involvement (e.g., 'on stage' or 'off stage'). "
            "Return the result in valid JSON format with keys 'location', 'location_change' (false since this is the first beat), and 'characters'."
        )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]
    
    response_text, cost = chat_with_gpt(messages, temperature=0.0)
    
    try:
        # Try to parse the JSON output.
        context_json = json.loads(response_text)
    except Exception as e:
        # If parsing fails, log or handle error appropriately.
        print("Failed to parse context agent output:", response_text)
        context_json = {}
    
    return context_json, cost

# ---------------------- Prose Agent ----------------------
def prose_agent(previous_passage, beat_a, beat_b, context_summary, temperature=0.3):
    system_message = (
        "You are ProseAgent, a creative writing assistant specialized in connecting narrative story beats. "
        "Current scene context: " + f"{context_summary}" + ". " +
        "Before writing, think through the key scene details: confirm the location and ensure all characters are actively engaged."
        "Before writing, outline the scene - confirm the previous details of the story and the current story beat, and make sure the story flows normally."
        "For instance, if a communication has ended - don't continue that conversation. Try not to repeat phrases too often, or start sentences with repetitive language."
        "Think about the story setting. What do physics allow? What is the mood and scene?"
        "Do not introduce new plot elements or extraneous details. Your final passage must be between 100 and 150 words."
    )
    
    if previous_passage:
        user_prompt = (
            f"Here is the previous narrative passage:\n\"{previous_passage}\"\n\n"
            f"This is the next story beat:\n\"{beat_b}\"\n\n"
            f"**Current Scene Context:** {context_summary}\n\n"
            "Please think through the scene details and then generate a connecting passage that continues the narrative seamlessly and in a way that makes narrative sense. "
            "Ensure your response is between 100 and 150 words."
        )
    else:
        user_prompt = (
            f"Here are two story beats:\nBeat A: \"{beat_a}\"\nBeat B: \"{beat_b}\"\n\n"
            f"**Current Scene Context:** {context_summary}\n\n"
            "Please think through the scene details first (confirm the location and character engagement), then generate a connecting narrative passage that bridges these beats creatively and seamlessly. "
            "Ensure your response is between 100 and 150 words."
        )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]
    
    return chat_with_gpt(messages, temperature=temperature)

def story_agent(passage, beats):
    """
    Checks whether the newly generated passage is fully consistent with the provided story beats.
    The passage is considered acceptable if it either reflects both beats or if it focuses solely on the second beat.
    The agent returns exactly "True" if the passage is consistent with these conditions (i.e. it faithfully reflects
    either both beats or solely the second beat without extraneous details), or "False" if it does not.
    """
    system_message = (
        "You are StoryAgent, a meticulous narrative consistency checker. Your task is to verify that the given passage "
        "faithfully reflects the intended narrative focus. The passage is acceptable if it either reflects both story beats "
        "or, at minimum, fully reflects the second beat. Do not allow extraneous details or hallucinations. "
        "After reviewing, return ONLY the single word 'True' if the passage meets these conditions, or ONLY 'False' if it does not."
    )
    
    # Build the user prompt.
    user_prompt = (
        f"Review the following passage:\n\"{passage}\"\n\n"
        "Against these story beats:\n"
    )
    for idx, beat in enumerate(beats, start=1):
        user_prompt += f"Beat {idx}: \"{beat}\"\n"
    user_prompt += (
        "\nThe passage is acceptable if it either reflects both beats or if it faithfully reflects only the second beat. "
        "Return ONLY 'True' if this is the case, otherwise return ONLY 'False'."
    )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]
    
    return chat_with_gpt(messages, temperature=0.0) 

def length_agent(passage, min_words=100, max_words=150):
    """
    Checks whether the newly generated passage meets the desired length.
    Return ONLY "True" if the passage has between min_words and max_words (inclusive),
    otherwise return ONLY "False".
    """
    system_message = (
        "You are LengthAgent, an expert in concise prose evaluation. Your task is to assess whether a given passage meets a specific word count requirement. "
        f"Return ONLY 'True' if the passage contains between {min_words} and {max_words} words (inclusive), or ONLY 'False' if it does not."
    )
    
    word_count = len(passage.split())
    user_prompt = (
        f"Examine the following passage:\n\"{passage}\"\n\n"
        f"It contains {word_count} words. "
        f"Return ONLY 'True' if the word count is between {min_words} and {max_words} inclusive, otherwise return ONLY 'False'."
    )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    return chat_with_gpt(messages, temperature=0.0)

def flow_agent(full_story, max_words=1500):
    system_message = (
        "You are FlowAgent, an expert in narrative refinement. You act as an editor for a creative writing magazine"
        "Your task is to review the entire story and improve its language flow and stylistic variation while maintaining the original plot and context."
        "Ensure that the narrative is engaging, that sentence structures are varied, and that the vocabulary is dynamic."
        "Avoid flowery language, adding detais or being verbose. Focus on enhancing the narrative's readability and coherence."
        "Check for dubious details. Do tools make sounds in space? Are the characters consistent? Are the locations accurate?"
        "Do not alter any factual details, change the location, or add new plot points—simply polish the text."
        "Try to maintain the original tone and mood of the story."
        "Do not exceed {max_words} in your edited version."
    )
    user_prompt = (
        f"Review the following story and improve its overall narrative flow, avoiding repetitive sentence structures and dull language:\n\n\"{full_story}\"\n\n"
        "Return the revised story. Make sure the context (location, characters, and story beats) remains consistent."
    )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]
    
    return chat_with_gpt(messages, max_tokens = int(4/3* max_words), temperature=0.0)
