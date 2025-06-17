# AGENT.md - Development Guidelines

## Build/Test/Lint Commands
- **Run project**: `python main.py` or `uv run main.py`
- **Install dependencies**: `uv sync` or `pip install -e .`
- **Python version**: Requires Python >=3.12 (see .python-version)

## Architecture & Structure
- **Single-file DSPy project**: Main logic in main.py
- **DSPy framework**: Uses DSPy >=2.6.27 for AI prompt engineering
- **Package manager**: Uses uv for dependency management (uv.lock present)
- **Virtual env**: Located in .venv/

## Code Style
- **Python standard**: Follow PEP 8 conventions
- **Function style**: Simple function definitions with clear naming
- **Entry point**: Use `if __name__ == "__main__":` pattern
- **Dependencies**: Add new deps via pyproject.toml dependencies array
- **DSPy imports**: Import DSPy modules as needed for prompt programming

## DSPy Learning Guidelines
- **Project goal**: Learning DSPy for building agents and LLM applications
- **Experimentation**: Feel free to add DSPy modules (dspy.Signature, dspy.Module, etc.)
- **LLM integration**: Configure LLM backends via dspy.configure() calls
- **Prompt engineering**: Use DSPy's declarative prompt programming approach
- **Testing patterns**: Add simple test functions to validate DSPy modules work

## Notes
- Learning-oriented project - prioritize experimentation over production patterns
- No formal tests yet - add quick validation functions as you build
- Document DSPy learnings and patterns in comments or README
