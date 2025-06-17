### **PRD: Local Unit Test Improver (`PyTestGen-LLM`) - Revised**

*   **Status:** Proposed
*   **Version:** 2.0
*   **Date:** 6/16/2025
*   **Author:** Manuel Porto

### 1. Introduction & Problem Statement

Writing comprehensive unit tests is crucial for software quality but is often a tedious and time-consuming task for developers. It's easy to miss edge cases, corner cases (e.g., `null` inputs, empty lists), or fail to cover all code paths.

Large Language Models (LLMs) excel at code generation, but their output can be unreliable, prone to "hallucination," and may not actually improve the test suite's quality. A developer cannot blindly trust a generated test case without a rigorous verification process.

This document outlines the requirements for `PyTestGen-LLM`, a local command-line tool that leverages LLMs to **automatically and reliably improve existing Python unit tests**. It is directly inspired by Meta's TestGen-LLM paper, adopting its core principles of **Assured LLM-based Software Engineering** and **ensemble-driven generation** to guarantee that any suggested test case is a measurable improvement.

### 2. Vision & Goal

The vision is to provide software engineers with a powerful, local-first support tool that reduces the manual effort of test suite enhancement through **ensemble learning** and **rigorous filtration**.

The primary goal is to create a CLI application that:
1.  Takes an existing Python test file as input.
2.  Uses **multiple LLM strategies in parallel** (ensemble approach) to generate diverse, relevant test cases.
3.  **Guarantees** that any added test case **builds correctly, passes reliably (non-flaky), and increases test coverage.**
4.  Provides **detailed coverage reporting** and **per-test-case guarantees**.
5.  Outputs actionable recommendations with telemetry for continuous improvement.

This tool is a **developer assistant**, not a replacement. It augments human intuition by systematically finding and validating test cases for missed logic paths.

### 3. User Persona

**Manuel, Software Engineer:**

*   **Goals:**
    *   Ship high-quality, robust, and well-tested code.
    *   Spend more time on feature development and less on boilerplate tasks.
    *   Ensure new code doesn't break existing functionality (prevent regressions).
    *   Achieve high test coverage efficiently.
*   **Pain Points:**
    *   Writing tests for every edge case (e.g., empty inputs, different data types, exceptions) is repetitive.
    *   Achieving high test coverage can be difficult and time-consuming.
    *   Using AI code generators is promising, but reviewing and trusting their output is risky and requires significant manual verification.
    *   Single-strategy AI approaches often miss unique test cases that other strategies might find.

`PyTestGen-LLM` will directly address these pain points by automating the generation *and verification* of valuable test cases using an ensemble approach.

### 4. Core Workflow & Features

The tool implements the **Assured LLM-based Software Engineering** pipeline with ensemble generation.

#### **End-to-End Ensemble Workflow:**

1.  **Input Processing:** The user invokes the tool pointing to a target test file and optionally the source file.
2.  **Ensemble Generation:** The tool runs **multiple strategies in parallel**:
    *   **Multiple prompts:** `extend_coverage`, `corner_cases`, `extend_test`, `statement_to_complete`
    *   **Multiple temperatures:** 0.0 (default), 0.2, 0.5 (or user-specified sweep)
    *   **Multiple LLMs:** If multiple LLMs are configured
3.  **Rigorous Filtration Pipeline:** Each candidate test case passes through automated filters:
    *   **Filter 1: Build/Syntax Check** 
    *   **Filter 2: Test Execution**
    *   **Filter 3: Flakiness Check (5-iteration test)**
    *   **Filter 4: Coverage Improvement Check**
    *   **Filter 5: Duplicate Detection**
4.  **Per-Test-Case Guarantees:** Each surviving test case comes with detailed metrics.
5.  **Ensemble Aggregation:** All candidates from different strategies that pass filtration are combined.
6.  **Detailed Reporting:** Coverage details, improvement metrics, and telemetry.

#### **Detailed Filtration Pipeline:**

```python
def filtration_pipeline(candidate_test):
    # Filter 1: Syntax/Build Check
    if not builds_correctly(candidate_test):
        log_telemetry("filter_1_fail", candidate_test)
        return None
    
    # Filter 2: Test Execution  
    if not passes_on_first_run(candidate_test):
        log_telemetry("filter_2_fail", candidate_test)
        return None
        
    # Filter 3: Flakiness Check (5 iterations)
    for i in range(5):
        if not run_test(candidate_test):
            log_telemetry("filter_3_fail_flaky", candidate_test)
            return None
    
    # Filter 4: Coverage Improvement
    coverage_delta = measure_coverage_improvement(candidate_test)
    if coverage_delta <= 0:
        log_telemetry("filter_4_fail_no_coverage", candidate_test)
        return None
        
    # Filter 5: Duplicate Detection  
    if is_duplicate_test(candidate_test):
        log_telemetry("filter_5_fail_duplicate", candidate_test)
        return None
        
    # Survived all filters
    log_telemetry("success", candidate_test, coverage_delta)
    return TestCase(candidate_test, coverage_delta)
```

#### **MVP Features (User Stories):**

*   **As a developer, I can** install the tool via `pip install pytestgen-llm`.
*   **As a developer, I can** configure the tool with my LLM API key via environment variables.
*   **As a developer, I can** run the tool in single-strategy mode:
    ```bash
    pytestgen-llm --test-file tests/test_user_model.py --source-file src/user_model.py
    ```
*   **As a developer, I can** run the tool in ensemble mode for maximum effectiveness:
    ```bash
    pytestgen-llm --test-file tests/test_user_model.py --source-file src/user_model.py --ensemble
    ```
*   **As a developer, I can** run temperature sweeps to find optimal settings:
    ```bash
    pytestgen-llm --test-file tests/test_user.py --temperature-sweep 0.0,0.2,0.5,1.0
    ```
*   **As a developer, I can** run on entire directories:
    ```bash
    pytestgen-llm --directory tests/ --ensemble
    ```
*   **As a developer, I want** the tool to output detailed diffs and coverage reports.
*   **As a developer, I want** per-test-case guarantees with specific coverage improvements.

#### **Technical Requirements:**

*   **Language:** Python 3.9+
*   **LLM Framework:** **DSPy** (for structured ensemble approach)
*   **Test Runner:** `pytest`
*   **Coverage Tool:** `coverage.py`
*   **LLM Support:** OpenAI, Anthropic, Google (extensible via DSPy)

### 5. DSPy Implementation Details

DSPy's structured approach is perfect for implementing the ensemble strategy from the paper.

#### **Multiple Prompt Signatures:**

```python
import dspy

class ExtendCoverageSignature(dspy.Signature):
    """
    Write additional pytest test functions to increase test coverage, 
    especially for corner cases missed by the original tests.
    """
    existing_test_class = dspy.InputField(desc="The source code of the existing pytest test class.")
    class_under_test = dspy.InputField(desc="The source code of the class being tested.")
    new_test_functions = dspy.OutputField(desc="A list of new, complete pytest test functions.")

class CornerCasesSignature(dspy.Signature):
    """
    Write additional pytest test functions that specifically target corner cases 
    and edge cases missed by the original test suite.
    """
    existing_test_class = dspy.InputField(desc="The source code of the existing pytest test class.")
    class_under_test = dspy.InputField(desc="The source code of the class being tested.")
    corner_case_tests = dspy.OutputField(desc="A list of pytest test functions targeting corner cases.")

class ExtendTestSignature(dspy.Signature):
    """
    Write additional pytest test functions to extend the existing test class
    with extra corner cases, based only on the test class structure.
    """
    existing_test_class = dspy.InputField(desc="The source code of the existing pytest test class.")
    extended_tests = dspy.OutputField(desc="A list of additional pytest test functions.")

class StatementCompleteSignature(dspy.Signature):
    """
    Complete the following statement by writing additional test functions.
    """
    existing_test_class = dspy.InputField(desc="The existing pytest test class.")
    class_under_test = dspy.InputField(desc="The class being tested.")
    completion_prompt = dspy.InputField(desc="Completion prompt for test generation.")
    completed_tests = dspy.OutputField(desc="A list of additional pytest test functions.")
```

#### **Ensemble Module Implementation:**

```python
class TestGenEnsemble(dspy.Module):
    def __init__(self):
        super().__init__()
        # Multiple strategy modules
        self.extend_coverage = dspy.Predict(ExtendCoverageSignature)
        self.corner_cases = dspy.Predict(CornerCasesSignature)
        self.extend_test = dspy.Predict(ExtendTestSignature)
        self.statement_complete = dspy.Predict(StatementCompleteSignature)
        
    def forward(self, test_class, source_class=None, strategies=None, temperatures=None):
        """
        Run ensemble generation across multiple strategies and temperatures.
        Returns a list of candidate test cases from all strategies.
        """
        strategies = strategies or ["extend_coverage", "corner_cases", "extend_test"]
        temperatures = temperatures or [0.0]
        
        all_candidates = []
        
        for strategy in strategies:
            for temp in temperatures:
                # Set temperature for this generation
                dspy.settings.configure(temperature=temp)
                
                try:
                    if strategy == "extend_coverage" and source_class:
                        result = self.extend_coverage(
                            existing_test_class=test_class,
                            class_under_test=source_class
                        )
                        all_candidates.extend(parse_test_functions(result.new_test_functions))
                        
                    elif strategy == "corner_cases" and source_class:
                        result = self.corner_cases(
                            existing_test_class=test_class,
                            class_under_test=source_class
                        )
                        all_candidates.extend(parse_test_functions(result.corner_case_tests))
                        
                    elif strategy == "extend_test":
                        result = self.extend_test(existing_test_class=test_class)
                        all_candidates.extend(parse_test_functions(result.extended_tests))
                        
                    # Log successful generation
                    log_telemetry("generation_success", strategy, temp, len(all_candidates))
                    
                except Exception as e:
                    log_telemetry("generation_error", strategy, temp, str(e))
                    continue
        
        return all_candidates
```

#### **Filtration and Execution Logic:**

```python
class TestGenLLM:
    def __init__(self):
        self.ensemble = TestGenEnsemble()
        self.coverage_baseline = None
        self.seen_tests = set()  # For duplicate detection
        
    def improve_test_file(self, test_file_path, source_file_path=None, 
                         ensemble=True, temperature_sweep=None):
        """Main entry point for test improvement."""
        
        # Load existing test and source code
        test_class = read_file(test_file_path)
        source_class = read_file(source_file_path) if source_file_path else None
        
        # Measure baseline coverage
        self.coverage_baseline = measure_coverage(test_file_path)
        
        # Generate candidates using ensemble approach
        if ensemble:
            strategies = ["extend_coverage", "corner_cases", "extend_test", "statement_to_complete"]
            temperatures = temperature_sweep or [0.0, 0.2, 0.5]
        else:
            strategies = ["extend_coverage"]
            temperatures = [0.0]
            
        candidates = self.ensemble.forward(
            test_class, source_class, strategies, temperatures
        )
        
        # Apply filtration pipeline
        surviving_tests = []
        for candidate in candidates:
            result = self.filtration_pipeline(candidate, test_file_path)
            if result:
                surviving_tests.append(result)
        
        # Generate detailed report
        return self.generate_report(surviving_tests, test_file_path)
        
    def filtration_pipeline(self, candidate_test, test_file_path):
        """Apply all 5 filters to a candidate test."""
        
        # Create temporary test file with candidate
        temp_test_file = create_temp_test_file(test_file_path, candidate_test)
        
        try:
            # Filter 1: Build Check
            if not self.builds_correctly(temp_test_file):
                log_telemetry("filter_1_fail", candidate_test)
                return None
            
            # Filter 2: Execution Check  
            if not self.passes_on_first_run(temp_test_file, candidate_test):
                log_telemetry("filter_2_fail", candidate_test)
                return None
                
            # Filter 3: Flakiness Check (5 iterations)
            if not self.flakiness_check(temp_test_file, candidate_test):
                log_telemetry("filter_3_fail_flaky", candidate_test)
                return None
            
            # Filter 4: Coverage Check
            coverage_improvement = self.coverage_check(temp_test_file)
            if coverage_improvement <= 0:
                log_telemetry("filter_4_fail_no_coverage", candidate_test)
                return None
                
            # Filter 5: Duplicate Check
            if self.is_duplicate(candidate_test):
                log_telemetry("filter_5_fail_duplicate", candidate_test)
                return None
                
            # Success! 
            test_result = TestCaseResult(
                test_code=candidate_test,
                coverage_improvement=coverage_improvement,
                lines_added=self.count_lines_added(temp_test_file),
                files_covered=self.get_files_covered(temp_test_file)
            )
            
            log_telemetry("success", candidate_test, coverage_improvement)
            self.seen_tests.add(self.normalize_test(candidate_test))
            return test_result
            
        finally:
            cleanup_temp_file(temp_test_file)
    
    def flakiness_check(self, temp_test_file, candidate_test, iterations=5):
        """Run the specific test 5 times to check for flakiness."""
        test_name = extract_test_name(candidate_test)
        
        for i in range(iterations):
            result = subprocess.run([
                "python", "-m", "pytest", temp_test_file + "::" + test_name, "-v"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return False  # Failed on iteration i
                
        return True  # Passed all 5 iterations
```

### 6. Success Metrics & Targets

Based on Meta's paper results, the tool should achieve:

#### **Primary Metrics:**
*   **Build Rate:** ≥75% of generated test cases should build correctly
*   **Pass Rate:** ≥55% of built test cases should pass reliably (non-flaky)  
*   **Coverage Rate:** ≥25% of passing test cases should increase coverage
*   **Overall Success Rate:** ~4-5% of total generation attempts should pass all filters

#### **Secondary Metrics:**
*   **Improvement Rate:** Percentage of test files for which the tool successfully generates ≥1 new test case
*   **Coverage Delta:** Average percentage point increase in line coverage per improved file
*   **Acceptance Rate:** (Qualitative) Developer acceptance of suggested changes in code review

#### **Ensemble Effectiveness:**
*   **Strategy Diversity:** Each prompt strategy should contribute unique test cases
*   **Temperature Optimization:** Track which temperature settings yield highest success rates per codebase

### 7. Enhanced CLI Design

```bash
# Basic single-strategy mode
pytestgen-llm --test-file tests/test_user.py --source-file src/user.py

# Ensemble mode (recommended) 
pytestgen-llm --test-file tests/test_user.py --source-file src/user.py --ensemble

# Custom strategy selection
pytestgen-llm --test-file tests/test_user.py --source-file src/user.py \
    --strategies extend_coverage,corner_cases

# Temperature sweep for optimization
pytestgen-llm --test-file tests/test_user.py --temperature-sweep 0.0,0.2,0.5,1.0

# Batch processing
pytestgen-llm --directory tests/ --ensemble --output-format json

# Evaluation mode (dry run with telemetry)
pytestgen-llm --test-file tests/test_user.py --evaluation-mode

# Custom configuration
pytestgen-llm --test-file tests/test_user.py --config pytestgen.yaml
```

#### **Configuration File Example:**

```yaml
# pytestgen.yaml
llms:
  primary: "gpt-4"
  secondary: "claude-3-sonnet" 
  
ensemble:
  strategies: ["extend_coverage", "corner_cases", "extend_test"]
  temperatures: [0.0, 0.2, 0.5]
  max_candidates_per_strategy: 5
  
filtration:
  flakiness_iterations: 5
  coverage_threshold: 0.0  # Any improvement counts
  
output:
  format: "diff"  # or "json", "file" 
  detailed_coverage: true
  telemetry: true
```

### 8. Observability & Learning

#### **Telemetry Collection:**

```python
def log_telemetry(event, *args, **kwargs):
    """Log detailed telemetry for optimization and analysis."""
    
    telemetry_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "session_id": get_session_id(),
        "test_file": kwargs.get("test_file"),
        "source_file": kwargs.get("source_file"),
        "strategy": kwargs.get("strategy"),
        "temperature": kwargs.get("temperature"), 
        "llm": kwargs.get("llm"),
        "result": kwargs.get("result"),
        "error": kwargs.get("error"),
        "coverage_delta": kwargs.get("coverage_delta"),
        "lines_added": kwargs.get("lines_added")
    }
    
    # Store locally and optionally send to analytics service
    append_to_log_file("~/.pytestgen/telemetry.jsonl", telemetry_entry)
```

#### **Analysis and Optimization:**

```bash
# Analyze which strategies work best for this codebase
pytestgen-llm --analyze --directory tests/

# Output: 
# Strategy Performance:
# - extend_coverage: 32% success rate, 2.1 avg lines covered
# - corner_cases: 28% success rate, 1.8 avg lines covered  
# - extend_test: 15% success rate, 1.2 avg lines covered
# 
# Recommended: Run with --strategies extend_coverage,corner_cases
```

### 9. Non-Functional Requirements

*   **Performance:** 
    *   Single file: <5 minutes (ensemble mode)
    *   Batch mode: Parallelizable across files
    *   Ensemble overhead: <2x single-strategy time
*   **Reliability:** 
    *   Zero false positives (no suggested test should break existing suite)
    *   Filtration pipeline must be robust and deterministic
*   **Usability:** 
    *   Clear progress indicators for ensemble runs
    *   Actionable error messages and suggestions
    *   Rich diff output with coverage annotations

### 10. Future Work (Post-MVP)

#### **DSPy Optimization Integration:**

```python
# Use DSPy's teleprompters to auto-optimize prompts
from dspy.teleprompt import BootstrapFewShot

def optimize_for_codebase(training_examples):
    """Auto-optimize prompts based on successful examples."""
    
    teleprompter = BootstrapFewShot(metric=coverage_improvement_metric)
    optimized_ensemble = teleprompter.compile(
        TestGenEnsemble(), 
        trainset=training_examples
    )
    return optimized_ensemble
```

#### **Advanced Features:**
*   **Mutation Testing Integration:** Use `mutmut` as the ultimate coverage quality filter
*   **Branch Coverage:** More sophisticated coverage metrics than line coverage  
*   **Smart Duplicate Detection:** Semantic similarity using AST analysis
*   **IDE Integration:** VS Code extension for in-editor test generation
*   **CI/CD Integration:** Automated test improvement in pull request workflows

### 11. Implementation Phases

**Phase 1 (MVP):** Basic ensemble generation + 5-filter pipeline
**Phase 2:** Full CLI with temperature sweeps and batch processing  
**Phase 3:** Telemetry, analysis, and optimization features
**Phase 4:** DSPy teleprompter integration for auto-optimization
**Phase 5:** Advanced features (mutation testing, IDE integration)
