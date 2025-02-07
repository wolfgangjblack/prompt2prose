from fastapi import FastAPI
from datetime import datetime
from utils import BeatToStory, StoryResponse, BeatConfig
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

beatbot = BeatToStory()
beatbot.setup_pipeline()

@app.get("/")
async def root():
    current_time = datetime.now().strftime("%H:%M %d-%m-%y")
    return {"message": f"""
    Welcome to the creative writing API! 
    The current time and date are {current_time}    
    Below are a list of commands available to users:
        GET / - Returns this message.
        GET /docs - Returns the API documentation - will redirect to the github README.
        GET /beat_to_story/ - Returns the agentic pipeline for beat to story generation, including agents, llms, and prompts.
        GET /metadata_to_story/ - Returns the agentic pipeline for metadata to story generation, including agents, llms, and prompts.
        POST /beat_to_story/generate. - Returns a json output with: a multi-agentic workflow story generated from a list of user provided beats, cost per agent in pipeline, story word count, and generation time.
        POST /metadata_to_story/generate/ - Returns a story generated from a list of user provided metadata.
    """}

@app.get("/beat_to_story/")
async def beat_to_story():
    return beatbot.describe_pipeline()

@app.get("/docs/")
async def docs():
    return RedirectResponse(url="https://github.com/wolfgangjblack/prompt2prose/blob/main/README.md")

@app.get("/metadata_to_story/")
async def metadata_to_story():
    return {"message": "This endpoint is under construction."}

@app.post("/beat_to_story/generate/", response_model = StoryResponse)
async def beat_to_story_generate(config: BeatConfig):
    
    start_time = datetime.now()
    
    beatbot.beats = config.beats
    beatbot.pipe()
    
    end_time = datetime.now()
    
    return StoryResponse(
        final_story = beatbot.edited_story,
        final_story_word_count = beatbot.story_length,
        generation_cost = beatbot.pipeline_cost(),
        generation_time = (end_time - start_time).total_seconds(),
        generation_metadata = beatbot.generation_metadata if config.gen_metadata_flag else {}
    )
        
@app.post("/metadata_to_story_generate/")
async def metadata_to_story_generate():
    return {"message": "This endpoint is under construction."}
