# prompt2prose
this repo contains code for llms to take in story beats and produce prose. 

This repo contains a dockerfile users can download alongside the code and run the experiment with prompt2pose models. This docker will serve users with an agentic workflow which will generate stories from beats or from metadata. 

## How to run
The container can be run as:

`docker run -e OPENAI_KEY-'your_openai_api_key' -p 8000:8000 prompt2pose`

This generates several endpoints meant to help aspiring writers flesh out stories and brainstorm creative writing.

### Endpoints

This work is divided into two main functionalities. 

#### BeatToStory

<i>Get Requests:</i>

<i>Post Requests:</i>


#### MetaToStory

