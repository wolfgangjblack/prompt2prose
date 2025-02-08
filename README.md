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
    "generation_cost": Dict,
    "generation_time": float,
    "generation_metadata": object (included if gen_metadata_flag=true)
}
```
#### MetaToStory

*Post Requests:*
- Endpoint: `/metadata_to_story/generate/`
- Method: POST
- Request Body:
```
json
{
    "beats": ["list of story beats"],
    "gen_metadata_flag": boolean (optional, default: false)
    "user_metadata": {
        "setting":
            {
                "location": "writer specified place",
                "notes": "about location/scene/chapter"
            },
            "genre": "genre writer is aiming for", #OPTIONAL - note: beats will have a stronger influence so if beats and genre are misaligned this may not work well
            "style": "style writer is aiming for", #OPTIONAL,
            "characters":
                {"name": Character name, "profile": A profile of that character},
                {...}
                }
}
```
- note: for now the fields of the user_metadata are fixed. We expect characters, setting info. If this is too rigid we can expand it. But for a POC, this was a good first pass
- Response Body:
```
{
    "final_story": "generated story text",
    "final_story_word_count": integer,
    "generation_cost": Dict,
    "generation_time": float,
    "generation_metadata": object (included if gen_metadata_flag=true)
}
```
