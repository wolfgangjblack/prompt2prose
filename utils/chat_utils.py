import os
from openai import OpenAI
from agents import prose_agent, story_agent, length_agent

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))

def chat_with_gpt(messages, max_tokens=400, temperature=0.3):
    """Calls the OpenAI Chat Completion API with the provided messages."""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return completion.choices[0].message.content.strip()

# ---------------------- Multi-Agent Story Generator ----------------------
def generate_story(beats, min_words=100, max_words=150, max_attempts=5):
    """
    Generates a complete story from a list of story beats.
    For each pair of beats:
      1. Use ProseAgent to generate a connecting passage.
      2. Use StoryAgent to verify consistency; if not, retry.
      3. Use LengthAgent to check that the passage meets length requirements; if not, retry.
    The process is recursive for each connecting passage until both checks return "True" or max_attempts is reached.
    
    Arguments:
      - beats: A list of story beat strings.
      - min_words, max_words: The desired word count range for connecting passages.
      - max_attempts: How many times to retry a connecting passage before giving up.
    
    Returns:
      - The final composed story as a string.
    """
    final_story = ""
    current_passage = None

    # For each pair of beats, generate and validate a connecting passage.
    for i in range(len(beats) - 1):
        beat_a = beats[i]
        beat_b = beats[i + 1]
        
        for attempt in range(max_attempts):
            generated_passage = prose_agent(current_passage, beat_a, beat_b)
            print(f"ProseAgent output (iteration {i+1}, attempt {attempt+1}):\n{generated_passage}\n")
            
            # Check consistency
            consistency = story_agent(generated_passage, [beat_a, beat_b])
            print(f"StoryAgent consistency check returned: {consistency}")
            if consistency != "True":
                print("Inconsistency detected; regenerating passage...\n")
                continue  # Rerun prose_agent
            
            # Check length
            length_ok = length_agent(generated_passage, min_words, max_words)
            print(f"LengthAgent check returned: {length_ok}")
            if length_ok != "True":
                print("Length requirement not met; regenerating passage...\n")
                continue  # Rerun prose_agent
            
            # If both checks pass, break out of the retry loop.
            break
        else:
            # If max_attempts were reached without both checks passing, raise an error or accept the last generated passage.
            print(f"Max attempts reached for beats {i+1}. Accepting the last generated passage.")
        
        final_story += f"{beat_a}\n{generated_passage}\n"
        current_passage = generated_passage  # Use current valid passage for continuity if needed.
    
    # Append the final beat.
    final_story += beats[-1]
    return final_story

