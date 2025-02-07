# prompt2prose
this repo contains code for llms to take in story beats and produce prose. 

This repo contains a dockerfile users can download alongside the code and run the experiment with prompt2pose models. This docker will serve users with an agentic workflow which will generate stories from beats or from metadata. 

## How to run
To run, users should install docker locally on their machine and make an account. Once docker in installed, the dockerfile must be built. To build this docker locally:

`docker build -t image_name:tag .`

Users should input their own `image_name`. I recommend `prompt2prose`

Once the docker is built, run the container with:

`docker run -e OPENAI_KEY='your_openai_api_key' -p 8000:8000 image_name`

This generates several endpoints meant to help aspiring writers flesh out stories and brainstorm creative writing.

### Endpoints

This work is divided into two main functionalities. 

#### BeatToStory

<i>Get Requests:</i>

<i>Post Requests:</i>


#### MetaToStory

