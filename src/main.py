from fastapi import FastAPI
from datetime import datetime
from utils import BeatToStory
from fastapi.middleware.cors import CORSMiddleware

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
        GET /beat_to_story/ - Returns the agentic pipeline for beat to story generation, including agents, llms, and prompts.
        GET /metadata_to_story/ - Returns the agentic pipeline for metadata to story generation, including agents, llms, and prompts.
        POST /beat_to_story_generate. - Returns a json output with: a multi-agentic workflow story generated from a list of user provided beats, cost per agent in pipeline, story word count, and generation time.
        POST /metadata_to_story_generate/ - Returns a story generated from a list of user provided metadata.
    """}

@app.get("/beat_to_story/")
async def beat_to_story():
    return beatbot.describe_pipeline()

@app.get("/metadata_to_story/")
async def metadata_to_story():
    return {"message": "This endpoint is under construction."}

@app.post("/beat_to_story_generate/")
async def beat_to_story_generate(BeatConfig):
    
    start_time = datetime.now()
    
    beatbot.pipe(BeatConfig.beats)
    
    end_time = datetime.now()
    
    if BeatConfig.gen_metadata_flag:
        return {"final_story": beatbot.story,
                "final_story_word_count": beatbot.story_length,
                "generation_cost": beatbot.pipeline_cost,
                "generation_time": end_time - start_time,
                "generation_metadata": beatbot.generation_metadata
                }
    
    else:
        return {"final_story": beatbot.story,
                "final_story_word_count": beatbot.story_length,
                "generation_cost": beatbot.pipeline_cost,
                "generation_time": end_time - start_time,
                }
        
@app.post("/metadata_to_story_generate/")
async def metadata_to_story_generate():
    return {"message": "This endpoint is under construction."}
