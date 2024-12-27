# LibreChat MCP server setup

This is a small setup that demonstrates how you can set up MCP servers with LibreChat

## Overview

This repo contains a `docker-compose.yml` and `librechat.yaml` that configures [LibreChat](https://www.librechat.ai/) with a few different [MCP](modelcontextprotocol.io) servers (in the `servers/` directory), in this case two simple ones (at the time of writing):
* A python/[FastMCP](https://github.com/jlowin/fastmcp) based [server](/servers/add/main.py) that exposes a single tool to add numbers (note that this style of MCP server declaration will be in the official [MCP python sdk](https://github.com/modelcontextprotocol/python-sdk) soon)
* A typescript based [server](/servers/brave-search/index.ts) that exposes a tool that allows the LLM to use the brave search engine. This requires an API key for brave. This is copied from the official servers, so check these [docs for API setup](https://github.com/modelcontextprotocol/servers/blob/main/src/brave-search/README.md)

## Requirements

You'll need [docker](https://docs.docker.com/engine/install/), with [docker compose](https://docs.docker.com/compose/install/). If you're on MacOS or Windows you'll probably need something like [docker desktop](https://www.docker.com/products/docker-desktop/).

## Setup

Make a copy of the `.env.example` file:

```sh
cp .env.example .env
```

And then [add in your Anthropic api key](https://www.librechat.ai/docs/configuration/pre_configured_ai/anthropic) (or OpenAI, but I haven't tested this out). And also configure the `BRAVE_API_KEY` for the `servers/brave-search` MCP server.

Once this is done, to start the server you should be able to run:

```sh
docker compose up -d --build
```

*Note: you might need to use `sudo`*

Then you should be able to go to https://localhost:3080/ to see LibreChat. Once you've signed up and made an account you should be able to configure an agent, and "add tools". On the second page of tools you should see our MCP tools! Save the agent and start a conversation with it to try out the MCP tools.

## Updating the MCP servers

You should be able to now add new tools to the existing MCP servers (or add whole new servers, but for that you'll need to update the `docker-compose.yml` and `librechat.yaml`) re-start the docker compose (`docker compose down && docker compose up -d --build`) and your changes should be present.
