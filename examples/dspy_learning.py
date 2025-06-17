"""
DSPy 101: A Learning Project for Building AI Agents with DSPy

This script demonstrates basic DSPy concepts by creating a simple question-answering agent
that uses OpenRouter as the language model provider. The example shows how to:

1. Configure DSPy with a language model (OpenRouter)
2. Define input/output signatures for structured prompts
3. Create DSPy modules for reasoning tasks
4. Chain modules together for complex workflows

DSPy is a framework that provides a structured way to program with language models
using "signatures" (input/output specifications) and "modules" (composable components).
"""

import os

import dspy

# === DSPy Signature Definitions ===
# Signatures in DSPy define the input and output structure for language model calls.
# They act like function signatures, specifying what the model should expect and return.


class QuestionAnswering(dspy.Signature):
    """
    A DSPy signature for basic question answering.

    DSPy signatures are classes that inherit from dspy.Signature and define:
    - Input fields: what information goes into the language model
    - Output fields: what we expect the model to produce
    - Docstring: provides context/instructions for the model

    This signature takes a question and produces a reasoned answer.
    """

    # Input field: the question to be answered
    question = dspy.InputField(desc="A question that needs to be answered")

    # Output field: the answer with reasoning
    answer = dspy.OutputField(desc="A clear, well-reasoned answer to the question")


class FactChecker(dspy.Signature):
    """
    A signature for checking if a statement contains factual information.

    This demonstrates how signatures can be used for different types of tasks
    beyond simple question-answering.
    """

    statement = dspy.InputField(desc="A statement to fact-check")
    is_factual = dspy.OutputField(
        desc="Whether the statement appears to be factual (Yes/No)"
    )
    explanation = dspy.OutputField(desc="Brief explanation of the assessment")


# === DSPy Module Definitions ===
# Modules in DSPy are composable components that use signatures to perform tasks.
# They can be chained together to create complex reasoning workflows.


class SimpleQA(dspy.Module):
    """
    A basic question-answering module using Chain of Thought reasoning.

    DSPy modules inherit from dspy.Module and define how to process inputs.
    This module uses ChainOfThought, which prompts the model to show its reasoning
    before providing the final answer.
    """

    def __init__(self):
        super().__init__()
        # ChainOfThought automatically adds reasoning steps before the final output
        self.generate_answer = dspy.ChainOfThought(QuestionAnswering)

    def forward(self, question: str):
        """
        The forward method defines how the module processes inputs.

        Args:
            question: The question to answer

        Returns:
            A dspy.Prediction object containing the answer and reasoning
        """
        # Call the Chain of Thought module with the question
        prediction = self.generate_answer(question=question)
        return prediction


class EnhancedQA(dspy.Module):
    """
    An enhanced QA module that combines question answering with fact checking.

    This demonstrates how to chain multiple DSPy modules together to create
    more sophisticated reasoning workflows.
    """

    def __init__(self):
        super().__init__()
        # Initialize both modules we'll use in the pipeline
        self.qa_module = dspy.ChainOfThought(QuestionAnswering)
        self.fact_checker = dspy.ChainOfThought(FactChecker)

    def forward(self, question: str):
        """
        Process a question through both QA and fact-checking.

        This shows how modules can be chained: the output of one becomes
        the input to another.
        """
        # First, get an answer to the question
        qa_result = self.qa_module(question=question)

        # Then, fact-check the answer
        fact_check_result = self.fact_checker(statement=qa_result.answer)

        # Return both results
        return dspy.Prediction(
            question=question,
            answer=qa_result.answer,
            is_factual=fact_check_result.is_factual,
            fact_check_explanation=fact_check_result.explanation,
        )


def setup_openrouter_lm() -> dspy.LM | None:
    """
    Configure DSPy to use OpenRouter as the language model provider.

    OpenRouter provides access to multiple language models through a single API.
    This function sets up the connection using an API key from environment variables.

    Returns:
        Configured DSPy language model or None if setup fails
    """
    # Get API key from environment variable
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not found!")
        print("Please set it with: export OPENROUTER_API_KEY='your-key-here'")
        return None

    try:
        # Create OpenRouter language model
        # We're using GPT-4o-mini as it's reliable and cost-effective
        lm = dspy.LM(
            model="openai/gpt-4o-mini",  # Model identifier for OpenRouter
            api_base="https://openrouter.ai/api/v1",  # OpenRouter API endpoint
            api_key=api_key,
            max_tokens=1000,  # Limit response length
            temperature=0.7,  # Control randomness (0.0 = deterministic, 1.0 = very random)
        )

        print(f"✅ Connected to OpenRouter with model: {lm.model}")
        return lm

    except Exception as e:
        print(f"❌ Failed to setup OpenRouter: {e}")
        return None


def demonstrate_basic_qa():
    """
    Demonstrate basic question-answering with DSPy.

    This shows the simplest DSPy workflow:
    1. Create a module
    2. Ask it a question
    3. Display the results
    """
    print("\n" + "=" * 50)
    print("🤖 Basic Question Answering Demo")
    print("=" * 50)

    # Create our QA module
    qa_module = SimpleQA()

    # Test questions
    questions = [
        "What is the capital of France?",
        "How does photosynthesis work?",
        "What are the benefits of using DSPy for AI programming?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)

        try:
            # Get the answer using our DSPy module
            result = qa_module(question)

            print(f"🎯 Answer: {result.answer}")

            # DSPy modules often include reasoning traces
            if hasattr(result, "rationale"):
                print(f"🧠 Reasoning: {result.rationale}")

            # Show the prompt history for debugging
            print("\n🔍 DEBUG: Prompt History")
            print("-" * 30)
            dspy.inspect_history(n=1)  # Show last prompt

        except Exception as e:
            print(f"❌ Error: {e}")


def demonstrate_enhanced_qa():
    """
    Demonstrate enhanced question-answering with fact-checking.

    This shows a more complex DSPy workflow where multiple modules
    work together to provide better results.
    """
    print("\n" + "=" * 50)
    print("🔍 Enhanced QA with Fact-Checking Demo")
    print("=" * 50)

    # Create our enhanced QA module
    enhanced_qa = EnhancedQA()

    # Test with questions that might have factual issues
    questions = [
        "When was the first iPhone released?",
        "How many moons does Mars have?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)

        try:
            # Get enhanced answer with fact-checking
            result = enhanced_qa(question)

            print(f"🎯 Answer: {result.answer}")
            print(f"✅ Factual Assessment: {result.is_factual}")
            print(f"📋 Fact Check Notes: {result.fact_check_explanation}")

            # Show detailed prompt history for this complex workflow
            print("\n🔍 DEBUG: Full Prompt History for Enhanced QA")
            print("-" * 45)
            dspy.inspect_history(n=2)  # Show last 2 prompts (QA + fact check)

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """
    Main function that orchestrates the DSPy learning demonstration.

    This function:
    1. Sets up the language model connection
    2. Configures DSPy to use that model
    3. Runs demonstration functions to show DSPy capabilities
    """

    print("🚀 Welcome to DSPy 101: Learning AI Agent Programming!")
    print("This script demonstrates core DSPy concepts with practical examples.")

    # Step 1: Setup the language model
    lm = setup_openrouter_lm()
    if not lm:
        print(
            "\n❌ Cannot proceed without a language model. Please check your API key."
        )
        return

    # Step 2: Configure DSPy to use our language model with debugging enabled
    # This tells DSPy which model to use for all subsequent operations
    # and enables tracing to see the actual prompts being generated
    dspy.configure(lm=lm)

    # Enable detailed tracing to see prompts and responses
    # This allows us to debug and understand how DSPy constructs prompts
    dspy.settings.configure(trace=[], show_guidelines=True)

    print("🔧 DSPy configured successfully with debugging enabled!")
    print("📊 You'll see the actual prompts DSPy generates after each example.")

    # Step 3: Run demonstrations
    try:
        # Basic QA demonstration
        demonstrate_basic_qa()

        # Enhanced QA demonstration
        demonstrate_enhanced_qa()

        print("\n" + "=" * 50)
        print("🎉 DSPy 101 Complete!")
        print("=" * 50)
        print("Key concepts demonstrated:")
        print("• 📋 Signatures: Define input/output structure")
        print("• 🧩 Modules: Composable reasoning components")
        print("• 🔗 Chaining: Connecting modules for complex workflows")
        print("• 🤖 LM Integration: Using external language models")
        print("• 🔍 Debugging: Inspecting generated prompts and traces")
        print(
            "\nNext steps: Explore DSPy optimizers, custom modules, and advanced agents!"
        )

        # Show complete history at the end for reference
        print("\n" + "=" * 50)
        print("🔍 COMPLETE PROMPT HISTORY")
        print("=" * 50)
        print("Here's a summary of all prompts generated during this session:")
        dspy.inspect_history()

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("This might be due to API issues or network connectivity.")


if __name__ == "__main__":
    main()
