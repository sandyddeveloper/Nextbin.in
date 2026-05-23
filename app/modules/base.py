from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAutomationModule(ABC):
    """
    Abstract Base Class for all Nextbin.in automation modules (Instagram, WhatsApp, Discord, Telegram).
    Enforces standardized lifecycle management and health reporting.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name identifier for the module.
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """
        Perform start-up initialization (load settings, compile rules, verify database connections).
        """
        pass

    @abstractmethod
    async def check_status(self) -> Dict[str, Any]:
        """
        Perform self-health checks and return a diagnostic dictionary.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Safely clean up any open client sessions, sockets, or thread-pools.
        """
        pass
