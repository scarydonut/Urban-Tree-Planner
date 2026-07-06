# Makefile for Urban Tree Planner

# Install dependencies
install:
	uv sync

# Run the ADK playground on port 18081
dev:
	uv run adk web --port 18081

# Run the MCP server (listening on 8090 by default)
run-mcp:
	uv run python -m app.mcp_server

# Lint the codebase with ruff
lint:
	ruff check .

# Run unit tests (if any)
test:
	pytest
