all: build deploy
build:
	poetry build
deploy: build
	python3 -m deployment.deploy
undeploy:
	python3 -m deployment.undeploy
register:
	curl -X POST \
	-H "Authorization: Bearer $$(gcloud auth print-access-token)" \
	-H "Content-Type: application/json" \
	-H "X-Goog-User-Project: sandbox-michael-menzel" \
	"https://discoveryengine.googleapis.com/v1alpha/projects/928871478446/locations/global/collections/default_collection/engines/agentspace-adk-tests_1752232618491/assistants/default_assistant/agents" \
	-d @deployment/agent-def.json
unregister:
	curl -X DELETE \
	-H "Authorization: Bearer $$(gcloud auth print-access-token)" \
	-H "Content-Type: application/json" \
	-H "X-Goog-User-Project: sandbox-michael-menzel" \
	"https://discoveryengine.googleapis.com/v1alpha/projects/928871478446/locations/global/collections/default_collection/engines/agentspace-adk-tests_1752232618491/assistants/default_assistant/agents/8833680602497461644"
local:
	adk web