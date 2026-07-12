"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Interface for language model providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate a text completion from the provider.

        Args:
            prompt: User or contextual prompt for the model.
            system_prompt: System-level instruction for the model.

        Returns:
            Generated text response from the provider.

        Raises:
            NotImplementedError: When called on the base implementation.
        """
        raise NotImplementedError("Subclasses must implement generate()")

    @abstractmethod
    async def generate_stream(self, prompt: str, system_prompt: str):
        """Stream a text completion from the provider.

        Args:
            prompt: User or contextual prompt for the model.
            system_prompt: System-level instruction for the model.

        Yields:
            Incremental chunks of generated text.

        Raises:
            NotImplementedError: When called on the base implementation.
        """
        raise NotImplementedError("Subclasses must implement generate_stream()")
