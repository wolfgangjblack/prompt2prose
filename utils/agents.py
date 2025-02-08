import json
from abc import ABC, abstractmethod
from typing import Any

from utils.llm_utils import chat_with_gpt


class Agent(ABC):
    def __init__(
        self, system_prompt: str, llm: str = "gpt-3.5-turbo", temperature: float = 0.0
    ):
        self.system_prompt = system_prompt
        self.token_cost = 0.0
        self.temperature = temperature
        self.llm = llm

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the agent's primary function
        """
        pass

    def describe(self) -> str:
        return f"{self.__class__.__name__}\n llm: {self.llm} -Note: Only GPT support atm \n Agentic Prompt:{self.system_prompt}\n"

    def get_cost(self):
        return self.token_cost


class ContextAgent(Agent):
    """
    ContextAgent is responsible for extracting key scene details from a story beat and comparing them with the previous scene context, if provided.
    Attributes:
        system_prompt (str): The system prompt that guides the agent's behavior.
    Methods:
        __init__():
            Initializes the ContextAgent with a predefined system prompt.
        __call__(beat, previous_context=None):
            Analyzes a beat and optionally compares it with the previous context.
            Returns a JSON-formatted summary of the scene, including setting, setting change status, and character details.
    """

    def __init__(self):
        super().__init__(
            system_prompt="""You are ContextAgent. Extract key scene details and validate physics/environment.
        Before generating JSON output:
        1. Check environmental consistency: Temperature, atmosphere, gravity, sound propagation
        2. Validate technology limitations and capabilities

        Return JSON with:
        1. setting: {
            location: current scene location,
            location_change: true only if location explicitly changes,
            important_details: key events, mood, or setting details
        }
        2. characters: list of characters with their status {
            name: character name,
            character_location: "on stage" or "off stage",
            status_change: true if role/presence changes
        }
        If no previous context, set change flags to false."""
        )

    def __call__(self, beat, previous_context=None):
        """
        Analyzes a beat and (optionally) compares it with the previous context.
        Returns a JSON-formatted summary of the scene, e.g.:
        {
        setting:
            {location: lunar surface,
                location_change: False,
                important_details: 'on the lunar surface, no sound or temperature unless inside somewhere'},
        characters:
            [{'name': 'Jack', 'character_location': 'on stage', 'status_change': False}, {'name': 'Xander', 'character_location': 'on stage', 'status_change': False}]}
        """
        # Build the user prompt. If previous_context exists, include it.
        if previous_context:
            user_prompt = (
                f"Previous Context (JSON):\n{previous_context}\n\n"
                f'New Beat:\n"{beat}"\n\n'
                "Compare the new beat to the previous context. If the new beat describes the same setting, mark 'location_change' as false; "
                "if it indicates a different location, mark it as true and update the 'setting' object."
                "For each character mentioned, compare with previous context: if their 'character_location' remains the same, mark 'status_change' as false; "
                "if it changes or a new character is introduced, mark it as true. "
                "Return the updated scene context in valid JSON format."
            )
        else:
            user_prompt = (
                f'New Beat:\n"{beat}"\n\n'
                "Extract the scene context. Identify the location and any characters along with their involvement (e.g., 'on stage' or 'off stage'). "
                "Return the result in valid JSON format with keys 'setting' and 'characters'."
            )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response_text, cost = chat_with_gpt(messages, temperature=self.temperature)

        try:
            # Try to parse the JSON output.
            context_json = json.loads(response_text)
        except Exception as e:
            # If parsing fails, log or handle error appropriately.
            print("Failed to parse context agent output:", response_text)
            context_json = {}

        self.token_cost += cost
        return context_json


class ProseAgent(Agent):
    def __init__(self, min_words: int = 100, max_words: int = 150):
        self.min_words = min_words
        self.max_words = max_words

        super().__init__(
            system_prompt="""You are ProseAgent, a creative writing assistant specialized in connecting narrative story beats.
        Current scene context: {context_summary}"""
            + f"""Before writing:
         1. Think through the key scene details: confirm the location and ensure all characters are actively engaged.
         2. outline the scene - confirm the previous details of the story and the current story beat, and make sure the story flows normally.
            - For instance if a communication has ended don't continue that conversation.
         3. Try not to repeat phrases too often, or start sentences with repetitive language.
         4. Think about the story setting. What do physics allow? What is the mood and scene?
        Do not introduce new plot elements or extraneous details.
        The final passage must be between {self.min_words} and {self.max_words} words.
        Aim closer to {self.max_words} words for a more detailed passage.""",
            temperature=0.3,
        )

    def __call__(self, previous_passage, beat_a, beat_b, context_summary):
        system_message = self.system_prompt.format(context_summary=context_summary)

        if previous_passage:
            user_prompt = (
                f'Here is the previous narrative passage:\n"{previous_passage}"\n\n'
                f'This is the next story beat:\n"{beat_b}"\n\n'
                f"**Current Scene Context:** {context_summary}\n\n"
                "Please think through the scene details and then generate a connecting passage that continues the narrative seamlessly and in a way that makes narrative sense. "
                "Ensure your response is between 100 and 150 words."
            )
        else:
            user_prompt = (
                f'Here are two story beats:\nBeat A: "{beat_a}"\nBeat B: "{beat_b}"\n\n'
                f"**Current Scene Context:** {context_summary}\n\n"
                "Please think through the scene details first (confirm the location and character engagement), then generate a connecting narrative passage that bridges these beats creatively and seamlessly. "
                "Ensure your response is between 100 and 150 words."
            )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ]

        response_text, cost = chat_with_gpt(messages, temperature=self.temperature)
        self.token_cost += cost
        return response_text


class StoryAgent(Agent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are StoryAgent, a narrative consistency checker. Your task is to verify that the given passage
        adequately moves the story forward between these beats. The passage should:
        1. Not contradict either beat
        2. Make logical progress from the first beat toward the second
        3. Not introduce major new elements not implied by the beats
        Return ONLY 'True' if these conditions are met, or ONLY 'False' if not.""",
            temperature=0.0,
        )

    def __call__(self, passage, beats):
        """
        Checks whether the newly generated passage is fully consistent with the provided story beats.
        The passage is considered acceptable if it either reflects both beats or if it focuses solely on the second beat.
        The agent returns exactly "True" if the passage is consistent with these conditions (i.e. it faithfully reflects
        either both beats or solely the second beat without extraneous details), or "False" if it does not.
        """

        # Build the user prompt.
        user_prompt = (
            f'Review the following passage:\n"{passage}"\n\n'
            "Against these story beats:\n"
        )
        for idx, beat in enumerate(beats, start=1):
            user_prompt += f'Beat {idx}: "{beat}"\n'
        user_prompt += (
            "\nThe passage is acceptable if it either reflects both beats or if it faithfully reflects only the second beat. "
            "Return ONLY 'True' if this is the case, otherwise return ONLY 'False'."
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response, cost = chat_with_gpt(messages, temperature=self.temperature)
        self.token_cost += cost
        return response


class LengthAgent(Agent):
    def __init__(self, min_words: int = 100, max_words: int = 150):
        super().__init__(
            system_prompt="""
        This is LengthAgent, a word count validator. Your task is to check whether the newly generated passage meets the desired length.
        Note: This does not use an AI model; it simply determines if the passage has between min_words and max_words (inclusive).
        """,
            llm=None,
        )
        self.min_words = min_words
        self.max_words = max_words

    def __call__(self, passage):
        """
        Checks whether the newly generated passage meets the desired length.
        Return ONLY "True" if the passage has between min_words and max_words (inclusive),
        otherwise return ONLY "False".
        """

        if self.min_words > self.max_words:
            raise ValueError("Minimum words cannot be greater than maximum words.")
        if self.min_words < 0 or self.max_words < 0:
            raise ValueError("Word counts cannot be negative.")
        if self.min_words == self.max_words:
            import warnings

            warnings.warn("Minimum and maximum word counts are the same.")

        word_count = len(passage.split())
        if word_count >= self.min_words and word_count <= self.max_words:
            return "True"
        else:
            return "False"


class FlowAgent(Agent):
    def __init__(self):
        super().__init__(
            system_prompt="""You are FlowAgent, an expert in narrative refinement. You act as a final editor for a creative writing team.
        Your task is to review the entire story and improve its language flow and stylistic variation while maintaining the original plot and context.
        Before rewriting the passage consider these points:
            - Ensure that the narrative is engaging
            - Are sentence structures varied and interesting
            - Avoid flowery language, adding detais or being verbose.
            - Focus on enhancing the narrative's readability and coherence.
            - Are the characters and plot consistent?
            - Do not alter any factual details, change the location, or add new plot points
            —simply polish the text.
            - Try to maintain the original tone and mood of the story.
            - Try to aim for around {max_words} in your edited version.
        Once you consider those points, return the revised story.""",
            temperature=0.0,
        )

    def __call__(self, full_story, max_words=1500):
        system_message = self.system_prompt.format(max_words=max_words)

        user_prompt = (
            f'Review the following story and improve its overall narrative flow, avoiding repetitive sentence structures and dull language:\n\n"{full_story}"\n\n'
            "Return the revised story. Make sure the context (location, characters, and story beats) remains consistent."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ]

        response_text, cost = chat_with_gpt(
            messages, max_tokens=int(4 / 3 * max_words + 50), temperature=0.0
        )
        self.token_cost += cost
        return response_text


class MetadataAgent(Agent):
    def __init__(self):
        super().__init__(
            system_prompt="""
        This is MetadataAgent, it takes metadata provided by the user
        and merges it with the context generated by the ContextAgent.
        Note: This does not use an AI model;
        """,
            llm=None,
        )

    def __call__(self, beat_to_story_context: dict, metadata: dict) -> None:
        """
        Updates context dictionary in-place with metadata
        Args:
            beat_to_story_context: The context dictionary from BeatToStory instance
            metadata: User provided metadata
        """
        for beat_num, context in beat_to_story_context.items():
            enriched_context = {
                "setting": {
                    "location": context["setting"]["location"],
                    "location_change": context["setting"]["location_change"],
                    "notes": metadata.get("setting", {}).get("notes", {}),
                    "important_details": context["setting"]["important_details"],
                },
                "characters": [],
            }

            metadata_chars = {
                char["name"]: char for char in metadata.get("characters", [])
            }

            for char in context["characters"]:
                enriched_char = {
                    "name": char["name"],
                    "character_location": char["character_location"],
                    "status_change": char["status_change"],
                }
                if char["name"] in metadata_chars:
                    enriched_char["profile"] = metadata_chars[char["name"]].get(
                        "profile", ""
                    )

                enriched_context["characters"].append(enriched_char)

            beat_to_story_context[beat_num] = enriched_context


class StyleGenreAgent(Agent):
    def __init__(self, style_guide: str):
        super().__init__(
            system_prompt=f"""You are an expert {style_guide} editor with decades of experience. Your job is to aggressively rewrite passages to match the {style_guide} style perfectly.

            When rewriting, consider:
            - Word choice and vocabulary specific to {style_guide}
            - Sentence structure and pacing typical of {style_guide}
            - Metaphors and descriptions that would appear in {style_guide}
            - Emotional tone and atmosphere characteristic of {style_guide}

            Examples of what this means:
            - For "noir": Use terse sentences, cynical tone, vivid sensory details, morally ambiguous descriptions
            - For "romance": Focus on emotional states, physical reactions, relationship dynamics, intimate observations
            - For "horror": Emphasize dread, use unsettling imagery, focus on tension and unease
            - For "adventure": Dynamic action verbs, quick pacing, emphasis on physical movement and environment
            - For "pirate english" : Use pirate slang, nautical terms, and a swashbuckling tone

            IMPORTANT: While maintaining the core story events and character actions, you should completely transform the STYLE of writing to match {style_guide}.""",
            temperature=0.7,  # Higher temperature for more creative variation
        )

    def __call__(self, passage: str, style_guide: str) -> str:
        user_prompt = (
            f'Rewrite this passage in pure {style_guide} style:\n"{passage}"\n\n'
            "Be bold with your stylistic changes while keeping the same basic events and character actions.\n"
            f"Maintain approximately {len(passage.split())} words."
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response_text, cost = chat_with_gpt(messages, temperature=self.temperature)
        self.token_cost += cost
        return response_text
