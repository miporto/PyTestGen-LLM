# PyTestGen-LLM

**Local Unit Test Improver using DSPy and Ensemble LLM Strategies**

PyTestGen-LLM is a powerful command-line tool that leverages Large Language Models (LLMs) to automatically and reliably improve existing Python unit tests. Inspired by Meta's TestGen-LLM paper, it uses ensemble learning and rigorous filtration to guarantee that any suggested test case is a measurable improvement.

## 🚀 Features

- **Ensemble Generation**: Uses multiple LLM strategies in parallel for diverse test case generation
- **Rigorous Filtration**: 5-stage quality pipeline ensures only valuable tests survive
- **Coverage Improvement**: Guarantees increased test coverage for all suggestions
- **Non-Flaky Tests**: Multi-iteration testing ensures reliability
- **Local-First**: Runs entirely on your machine with your choice of LLM provider
- **Professional CLI**: Rich terminal interface with progress tracking

## 📋 Requirements

- Python ≥3.12
- uv package manager
- LLM API access (OpenAI, Anthropic, etc.)

## 🛠️ Installation

### From Source (Development)

```bash
# Clone the repository
git clone <repository-url>
cd pytestgen-llm

# Install with uv
uv sync --all-extras

# Install the package in development mode
uv pip install -e .
```

### Via pip (Once Published)

```bash
pip install pytestgen-llm
```

## 🎯 Quick Start

1. **Configure your LLM provider**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   # or
   export ANTHROPIC_API_KEY="your-api-key"
   ```

2. **Improve a test file**:
   ```bash
   pytestgen-llm --test-file tests/test_user.py --source-file src/user.py
   ```

3. **Use ensemble mode for best results**:
   ```bash
   pytestgen-llm --test-file tests/test_user.py --source-file src/user.py --ensemble
   ```

## 🔧 Usage Examples

### Basic Single Strategy
```bash
pytestgen-llm --test-file tests/test_user_model.py --source-file src/user_model.py
```

### Ensemble Mode (Recommended)
```bash
pytestgen-llm --test-file tests/test_user.py --source-file src/user.py --ensemble
```

### Temperature Sweep
```bash
pytestgen-llm --test-file tests/test_user.py --temperature-sweep 0.0,0.2,0.5,1.0
```

### Batch Processing
```bash
pytestgen-llm --directory tests/ --ensemble --output-format json
```

### Dry Run (Evaluation Mode)
```bash
pytestgen-llm --test-file tests/test_user.py --evaluation-mode
```

## 🏗️ Architecture

PyTestGen-LLM implements the **Assured LLM-based Software Engineering** pipeline:

1. **Ensemble Generation**: Multiple strategies (extend_coverage, corner_cases, extend_test, statement_complete)
2. **Rigorous Filtration**: 5-stage pipeline (syntax, execution, flakiness, coverage, duplicates)
3. **Quality Guarantees**: Each surviving test increases coverage and passes reliably

### Success Metrics (Based on Meta's Research)
- **Build Rate**: ≥75% of generated tests build correctly
- **Pass Rate**: ≥55% of built tests pass reliably
- **Coverage Rate**: ≥25% of passing tests increase coverage
- **Overall Success**: ~4-5% of total attempts pass all filters

## 🧪 Development

### Setup Development Environment

```bash
# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run ty .
```

### Project Structure

```
pytestgen-llm/
├── src/pytestgen_llm/          # Main package
│   ├── core/                   # Ensemble and signatures
│   ├── filters/                # Filtration pipeline
│   ├── cli/                    # Command-line interface
│   ├── utils/                  # File and coverage utilities
│   └── telemetry/              # Analytics and optimization
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data
└── examples/                   # Usage examples
```

## 📊 Performance

- **Single file**: <5 minutes (ensemble mode)
- **Batch mode**: Parallelizable across files
- **Memory efficient**: Optimized for large codebases
- **API cost aware**: Configurable limits and optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Phases

- **Phase 1 (MVP)**: ✅ Basic ensemble generation + 5-filter pipeline
- **Phase 2**: 🚧 Full CLI with temperature sweeps and batch processing  
- **Phase 3**: 📋 Telemetry, analysis, and optimization features
- **Phase 4**: 🔮 DSPy teleprompter integration for auto-optimization
- **Phase 5**: 🚀 Advanced features (mutation testing, IDE integration)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by Meta's [TestGen-LLM paper](https://arxiv.org/abs/2302.01560) and the principles of Assured LLM-based Software Engineering.

Built with [DSPy](https://github.com/stanfordnlp/dspy) for structured LLM programming.

---

**Status**: 🚧 Alpha - Active Development

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/username/pytestgen-llm).
