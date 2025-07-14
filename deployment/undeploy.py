from dotenv import load_dotenv

load_dotenv()

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp



def main():
    """Initializes and deploys the StyleScene agent."""
    vertexai.init(staging_bucket="gs://sandbox-michael-menzel-adk-staging-us-central1")

    agent_name = "StyleScene Agent"

    existing_agents = list(agent_engines.list(filter=f'display_name="{agent_name}"'))
    for agent in existing_agents:
        agent.delete(force=True)
    
    print("\n=== Undeployment successful! ===")


if __name__ == "__main__":
    main()
