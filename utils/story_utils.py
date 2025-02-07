from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from utils.agents import Agent, ContextAgent, FlowAgent, LengthAgent, ProseAgent, StoryAgent

class BeatToStory(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    min_words_per_beat: int = 100
    max_words_per_beat: int = 150
    max_attempts_per_beat: int = 10
    story: Optional[str] = ''
    edited_story: Optional[str] = ''
    beats: List[str] = []
    context: Dict[int, str] = {}
    generation_metadata: Dict[int, Any] = {}
    agents: Dict[str, Agent] = {}
        
    def setup_pipeline(self, agents: Dict[str, Agent] | None = None):
        """
        Initialize agents for the story pipeline.
        Can either use default agents or accept custom agents.
        """
        if agents is None:
            self.agents = {
                "context": ContextAgent(),
                "prose": ProseAgent(min_words=self.min_words_per_beat, 
                             max_words=self.max_words_per_beat),
                "story": StoryAgent(),
                "length": LengthAgent(min_words=self.min_words_per_beat, 
                                    max_words=self.max_words_per_beat),
                "flow": FlowAgent()
            }
        else:
            self.agents = agents
    
    def describe_pipeline(self):
            """Return description of all agents in pipeline order"""
            return "\n\n".join(self.agents[name].describe() for name in self.agents.keys())
    
    def pipeline_cost(self):
        """Return cost of all agents in pipeline order"""
        cost_dict = {name: self.agents[name].token_cost for name in self.agents.keys()}
        cost_dict["total"] = sum(cost_dict.values())
        return cost_dict

    def get_context(self, verbose = False):
        """
        Generates a context for each beat in the story. This context is used by the prose_agent to generate a connecting passage.
        This operates as story metadata that is created by the beats and is meant to help outline the scene and story logic. 
        Arguments:
        - beats: A list of story beat strings.
        - context: A dictionary of context strings for each beat.
        - context_agent: An agent that generates context for a given beat.
        
        Returns:
        - A dictionary of context strings for each beat.
        """
       # For each pair of beats, generate and validate a connecting passage.
        if not self.beats: 
            raise ValueError("No beats provided. Please add beats before generating story.")
        
        previous_context = None
        if verbose:
            print("Generating context from beats...")
        for i in range(len(self.beats) - 1):
            if verbose:
                print(f"    crafting context on beat {i}")
            context = self.agents["context"](self.beats[i], previous_context)
            self.context[i] = context
            previous_context = context

    def generate_story(self, verbose = False):
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
        self._check_state()
        current_passage = None
        
        # For each pair of beats, generate and validate a connecting passage.
        if verbose:
            print("Generating story from beats...")
        for i in range(len(self.beats) - 1):
            beat_a = self.beats[i]
            beat_b = self.beats[i + 1]
            
            for idx, _ in enumerate(range(self.max_attempts_per_beat)):
                generated_passage = self.agents["prose"](current_passage, beat_a, beat_b, context_summary=self.context[i])
                if verbose:
                    print(f"    ProseAgent output (iteration {i+1}, attempt {idx+1}):\n{generated_passage}\n")
                consistency = self.agents['story'](generated_passage, [beat_a, beat_b])
                # print(f"StoryAgent consistency check returned: {consistency}")
                if consistency != "True":
                    if verbose:
                        print(f"        beat {i} | attempt: {idx} | Inconsistency detected; regenerating passage...")
                    continue  # Rerun prose_agent
                # Check length
                length_ok = self.agents['length'](generated_passage)
                #
                if not length_ok:
                    if verbose:
                        print(f"        beat {i} | attempt: {idx} | Length requirement not met {len(generated_passage.split())}; regenerating passage...")
                    continue  # Rerun prose_agent
                
                # If both checks pass, break out of the retry loop.
                self.generation_metadata["beat_" + str(i)] = {
                    "attempts": idx + 1,
                    "passage": generated_passage,
                    "passage_length": len(generated_passage.split()),
                    "exceeded_max_attempts": idx + 1 == self.max_attempts_per_beat
                }
                break
            else:
                # If max_attempts were reached without both checks passing, raise an error or accept the last generated passage.
                if verbose:
                    print(f"Max attempts reached for beats {i}. Accepting the last generated passage.")
            
            self.story += f"{generated_passage}\n"
            current_passage = generated_passage  # Use current valid passage for continuity if needed.
        # Append the final beat.
        return self.story
    
    def edit_story(self, verbose = False):
        """
        Edits story by adding in the flow_agent
        arguments:
        - verbose: If True, prints out the steps of the story editing process
        """
        if self.story == "":
            raise ValueError(f"Story is empty. Please use {self.__class__.__name__}.generate_story first or run {self.__class__.__name__}.pipe() to generate a story.")
        
        if verbose:
            print("Editing story...")
        self.edited_story = self.agents['flow'](self.story, self.max_words_per_beat * len(self.beats))
        
        return self.edited_story

    def pipe(self, verbose = False):
        """
        Generates a complete edited story using the agents we've designed above. 
        This improves upon the final story generated by generate_story by adding
        in the flow_agent
        """
        state = self._check_state()
        if state != "OK":
            if verbose:
                print(f"Note: {state}")
        
        if self.context == {}:
            self.get_context(verbose=verbose)
        
        if self.story == "":
            self.generate_story(verbose=verbose)

        if verbose:
            print("Editing story...")
        self.edit_story()

        return self.edited_story
    
    def _check_state(self):
        errors = []

        if not self.agents:
            errors.append("No agents provided. Run setup_pipeline() first.")
        
        if not self.beats:
            errors.append("No beats provided. Add beats before continuing.")
        
        if self.context == {} and self.story:
            errors.append("Story was generated without context. Run get_context() first.")
        
        if self.story and not self.edited_story:
            return "Story generated but not edited. Run edit_story() to complete the process."
            
        if errors:
            raise ValueError("\n".join(errors))
        
        return "OK"
    
    @property
    def story_length(self) -> int:
        """Returns the length of the edited story in words."""
        return len(self.edited_story.split()) if self.edited_story else 0