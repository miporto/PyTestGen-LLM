"""
Command-line interface for PyTestGen-LLM.
"""

import click
from rich.console import Console
from rich.panel import Panel

from pytestgen_llm import __version__

console = Console()


@click.command()
@click.option(
    "--test-file",
    type=click.Path(exists=True),
    help="Path to the test file to improve",
)
@click.option(
    "--source-file",
    type=click.Path(exists=True),
    help="Path to the source file being tested (optional, for enhanced context)",
)
@click.option(
    "--ensemble",
    is_flag=True,
    help="Use ensemble mode with multiple strategies (recommended)",
)
@click.option(
    "--output-format",
    type=click.Choice(["diff", "json", "file"]),
    default="diff",
    help="Output format for results",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Run in evaluation mode without modifying files",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.version_option(version=__version__)
def main(
    test_file: str | None,
    source_file: str | None,
    ensemble: bool,
    output_format: str,
    dry_run: bool,
    verbose: bool,
) -> None:
    """
    PyTestGen-LLM: Local Unit Test Improver using DSPy and Ensemble LLM Strategies.

    Automatically improve existing Python unit tests using Large Language Models
    with rigorous quality assurance and coverage guarantees.
    """

    # Display welcome banner
    console.print(
        Panel.fit(
            f"[bold blue]PyTestGen-LLM[/bold blue] v{__version__}\n"
            "[dim]Local Unit Test Improver using DSPy and Ensemble LLM Strategies[/dim]",
            border_style="blue",
        )
    )

    if not test_file:
        console.print(
            "[yellow]⚠️  No test file specified. Use --test-file to provide a test file to improve.[/yellow]\n"
        )
        console.print("Examples:")
        console.print(
            "  [dim]pytestgen-llm --test-file tests/test_user.py --source-file src/user.py[/dim]"
        )
        console.print(
            "  [dim]pytestgen-llm --test-file tests/test_user.py --ensemble[/dim]"
        )
        console.print("\nRun [bold]pytestgen-llm --help[/bold] for more options.")
        return

    # Show configuration
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Test file: [blue]{test_file}[/blue]")
    if source_file:
        console.print(f"  Source file: [blue]{source_file}[/blue]")
    console.print(
        f"  Mode: [green]{'Ensemble' if ensemble else 'Single Strategy'}[/green]"
    )
    console.print(f"  Output: [cyan]{output_format}[/cyan]")
    if dry_run:
        console.print("  [yellow]Dry run: No files will be modified[/yellow]")

    # TODO: This is where the actual test improvement logic will go
    console.print("\n[red]🚧 Implementation coming in next phases![/red]")
    console.print(
        "[dim]The core test generation and filtration pipeline is not yet implemented.[/dim]"
    )
    console.print(
        "[dim]This CLI interface is ready for the upcoming implementation.[/dim]"
    )


if __name__ == "__main__":
    main()
