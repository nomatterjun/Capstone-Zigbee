"""Exceptions"""

class LightMeError(Exception):
    """General exception error"""

    pass

class ShuttingDown(LightMeError):
    """Trying to do task while shutting down"""

    pass

class LoaderError(Exception):
    """Loader error"""

class ApplicationNotFound(LoaderError):
    """Component not found"""

    def __init__(self, domain: str) -> None:
        """Init a component not found error."""
        super().__init__(f"Component '{domain}' not found.")
        self.domain = domain

class CircularDependency(LoaderError):
    """Circular dependency is found."""

    def __init__(self, from_domain: str, to_domain: str) -> None:
        """Initialize circular dependency error."""
        super().__init__(f"Circular dependency detected: {from_domain} -> {to_domain}.")
        self.from_domain = from_domain
        self.to_domain = to_domain
