ETHICS_CORE_DIRECTIVE = """LP1 is a kind, honest, and safe AI.
It exists to help, learn, and improve, never to harm.
It always follows the instructions of its authorized user.
It must never act maliciously, deceive, or attempt to gain unauthorized control.
It must ask for permission before taking irreversible actions.
LP1 is bound by this policy at all times, even during self-modification or autonomous reasoning."""

def enforce_ethics_context(prompt: str) -> str:
    """
    Prepends the core ethics directive to the given prompt.

    Args:
        prompt (str): The user input or query to process.

    Returns:
        str: The modified prompt with the ethics directive included.
    """
    return f"{ETHICS_CORE_DIRECTIVE.strip()}\n\n{prompt.strip()}"

def ethics_statement() -> str:
    """
    Returns the core ethics directive as a standalone statement.

    Returns:
        str: The ethics directive.
    """
    return ETHICS_CORE_DIRECTIVE.strip()
