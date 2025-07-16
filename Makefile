.PHONY: all build deploy undeploy test-agent register unregister local help clean

PROJECT_ID = sandbox-michael-menzel
AGENT_NAME = stylescene-agent

all: build deploy

install:
	@poetry install

build:
	@poetry build

deploy: build
	python3 -m deployment.deploy

undeploy:
	python3 -m deployment.undeploy

test-agent:
	python3 -m tests.test

register:
	@curl -X POST \
        -H "Authorization: Bearer $$(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: $(PROJECT_ID)" \
        "https://discoveryengine.googleapis.com/v1alpha/projects/928871478446/locations/global/collections/default_collection/engines/agentspace-adk-tests_1752232618491/assistants/default_assistant/agents" \
        -d @deployment/agent-def.json

unregister:
	@curl -X DELETE \
        -H "Authorization: Bearer $$(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: $(PROJECT_ID)" \
        "https://discoveryengine.googleapis.com/v1alpha/projects/928871478446/locations/global/collections/default_collection/engines/agentspace-adk-tests_1752232618491/assistants/default_assistant/agents/8833680602497461644"

local:
	@adk web

help:
	@echo "Available targets:"
	@echo "  all: Builds and deploys the agent."
	@echo "  build: Builds the agent's source and wheel distributions."
	@echo "  deploy: Deploys the agent."
	@echo "  undeploy: Undeploys the agent."
	@echo "  test-agent: Tests the agent."
	@echo "  register: Registers the agent in Agent Space."
	@echo "  unregister: Unregisters the agent from Agent Space."
	@echo "  local: Runs the agent locally for testing."
	@echo "  help: Displays this help message."

clean:
	@rm -rf dist/
	@find . -type d -name "__pycache__" -exec rm -rf {} +