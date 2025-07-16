# stylescene-agent
An agent allowing to redress persons, modify the scene, and animate as video

## Development and Usage

This project uses `make` to streamline common development tasks.

### Prerequisites

Before you begin, ensure you have the following installed:
- Python (version 3.11+ recommended)
- Poetry for dependency management
- `make`

### Setup

1.  Clone the repository and navigate into the project directory.
2.  Install the required dependencies, which will also create a virtual environment:
    ```bash
    make install
    ```

### Makefile Commands

The following commands are available to manage the agent lifecycle:
- `make build`: Builds the agent's source and wheel distributions.
- `make deploy`: Deploys the agent using the Google Agent Development Kit (ADK).
- `make register`: Registers the agent in Agent Space.
- `make unregister`: Unregisters the agent from Agent Space.
- `make test`: Runs the project's test suite using `pytest`.
- `make test-agent`: Tests the agent locally and remote with validation tasks.
- `make clean`: Removes all build artifacts and cache directories.
