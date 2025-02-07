# prompt2prose
this repo contains code for llms to take in story beats and produce prose. 

This repo contains a dockerfile users can download alongside the code and run the experiment with prompt2pose models. This docker will serve users with an agentic workflow which will generate stories from beats or from metadata. 

## How to run
To run, users should install docker locally on their machine and make an account. Once docker in installed, the dockerfile must be built. To build this docker locally:

`docker build -t image_name .`

Users should input their own `image_name`. I recommend `prompt2prose`

Once the docker is built, run the container with:

`docker run -e OPENAI_KEY='your_openai_api_key' -p 8000:8000 image_name`

This generates several endpoints meant to help aspiring writers flesh out stories and brainstorm creative writing.

### Endpoints

This work is divided into two main functionalities. 

#### Base Gets
- `GET /` - Returns welcome message and list of available endpoints
- `GET /docs` - Redirects to this documentation
- `GET /beat_to_story/` - Returns details about the beat-to-story generation pipeline
- `GET /metadata_to_story/` - Returns details about metadata-to-story generation pipeline (under construction)

#### BeatToStory


*Get Requests:*
- `/beat_to_story/` - Returns pipeline information including agents, LLMs, and prompts used in story generation

*Post Requests:*
- Endpoint: `/beat_to_story/generate/`
- Method: POST
- Request Body:
```
json
{
    "beats": ["list of story beats"],
    "gen_metadata_flag": boolean (optional, default: false)
}
```
- Response Body:
```
{
    "final_story": "generated story text",
    "final_story_word_count": integer,
    "generation_cost": float,
    "generation_time": float,
    "generation_metadata": object (included if gen_metadata_flag=true)
}
```
#### MetaToStory

<i> Currently under construction </i>