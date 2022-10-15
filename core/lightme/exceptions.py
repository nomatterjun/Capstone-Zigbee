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
