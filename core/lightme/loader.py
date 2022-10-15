"""Methods for loading LightMe drivers."""
from __future__ import annotations

import asyncio
import importlib
import json
import logging
import pathlib
import sys

from collections.abc import Iterable
from types import ModuleType
from typing import Literal, TypedDict, cast
from termcolor import colored

from .core import LightMe
from .exceptions import ApplicationNotFound

COMPONENTS = "components"
APPLICATIONS = "applications"
BUILTIN = "lightme.components"

_UNDEF = object() # Undefined object.

_LOGGER = logging.getLogger(__name__)

class Manifest(TypedDict, total=False):
    """
    Application manifest.
    """

    name: str
    domain: str
    driver_type: Literal["application", "helper"]
    requirements: list[str]
    user_default: bool
    mqtt: list[str]

class Application:
    """Application in LightMe."""

    def __init__(
        self,
        lightme: LightMe,
        pkg_path: str,
        file_path: pathlib.Path,
        manifest: Manifest
    ) -> None:
        """Init a new application."""
        self.lightme = lightme
        self.pkg_path = pkg_path
        self.file_path = file_path
        self.manifest = manifest

        _LOGGER.info("Loaded %s from %s", self.domain, pkg_path)
        print(f"Loaded {self.domain} from {pkg_path} - [loader.py: Application:__init__]")

    @property
    def name(self) -> str:
        """Name."""
        return self.manifest["name"]

    @property
    def domain(self) -> str:
        """Domain."""
        return self.manifest["domain"]

    @property
    def requirements(self) -> list[str]:
        """Requirements."""
        return self.manifest.get("requirements", [])

    @property
    def user_default(self) -> bool:
        """User Default."""
        return self.manifest.get("user_default") or False

    @classmethod
    def resolve_from_root(
        cls, lightme: LightMe, root_module: ModuleType, domain: str
    ) -> Application | None:
        """Resolve application from root module."""

        for base in root_module.__path__:
            manifest_path = pathlib.Path(base) / domain / "manifest.json"
            print(
                colored(f"Manifest Path: {manifest_path} - [loader.py: resolve_from_root]", 'white')
            )

            if not manifest_path.is_file():
                continue

            try:
                manifest = json.loads(manifest_path.read_text())
            except ValueError as error:
                _LOGGER.error(
                    "Error parsing manifest.json file at %s: %s", manifest_path, error
                )
                continue

            # application itself. (using class method)
            application = cls(
                lightme,
                f"{root_module.__name__}.{domain}",
                manifest_path.parent,
                manifest
            )
            return application

        return None

    def get_component(self) -> ModuleType:
        """Return component."""

        cache: dict[str, ModuleType] = self.lightme.data.setdefault(COMPONENTS, {})

        # If domain's already in cache, return it.
        if self.domain in cache:
            return cache[self.domain]

        try:
            cache[self.domain] = importlib.import_module(self.pkg_path)
        except ImportError:
            raise
        except Exception as error:
            _LOGGER.exception(
                "Exception importing component %s", self.pkg_path
            )
            raise ImportError(f"Exception importing {self.pkg_path}") from error

        return cache[self.domain]

    def __repr__(self) -> str:
        """Representation of class."""
        return f"<Application {self.domain}: {self.pkg_path}>"


def _resolve_application_from_root(
    lightme: LightMe, root_module: ModuleType, domains: list[str]
) -> dict[str, Application]:
    """Resolve multiple applications from root."""

    applications: dict[str, Application] = {}
    for domain in domains:
        try:
            application = Application.resolve_from_root(lightme, root_module, domain)
        except Exception: # pylint: disable=broad-except
            _LOGGER.exception("Error loading application: %s", domain)
        else:
            if application:
                applications[domain] = application
    return applications

async def async_get_application(lightme: LightMe, domain: str) -> Application:
    """Get an application."""

    if isinstance(domain, set):
        domain = domain.pop()
    applications_or_excs = await async_get_applications(lightme, [domain])
    application = applications_or_excs[domain]
    if isinstance(application, Application):
        return application
    raise application

async def async_get_applications(
    lightme: LightMe, domains: Iterable[str]
) -> dict[str, Application | Exception]:
    """Get application."""

    # Set cache from lightme.data with key "applications".
    # if None, create empty one.
    if (cache := lightme.data.get(APPLICATIONS)) is None:
        if not _async_mount_config_dir(lightme):
            return {domain: ApplicationNotFound(domain) for domain in domains}
        cache = lightme.data[APPLICATIONS] = {}

    results: dict[str, Application | Exception] = {}
    needed: dict[str, asyncio.Event] = {}
    evt_in_progress: dict[str, asyncio.Event] = {}

    for domain in domains:
        app_or_evt: Application | asyncio.Event | None = cache.get(domain, _UNDEF)
        if isinstance(app_or_evt, asyncio.Event):
            # If app_or_evt is asyncio Event, put them in evt_in_progress list.
            evt_in_progress[domain] = app_or_evt
        elif app_or_evt is not _UNDEF:
            # Else if app_or_evt has default value(_UNDEF), cast it as Application.
            results[domain] = cast(Application, app_or_evt)
        elif "." in domain:
            # Else if domain contains '.', it's invalid so raise error.
            results[domain] = ValueError(f"Invalid domain {domain}")
        else:
            # Else
            needed[domain] = cache[domain] = asyncio.Event()

    # If cache has Event member
    if evt_in_progress:
        await asyncio.gather(
            *[event.wait() for event in evt_in_progress.values()]
        )
        for domain in evt_in_progress:
            # Even if core waited but still it's _UNDEF, it doesn't exist.
            if (app_or_evt := cache.get(domain, _UNDEF)) is _UNDEF:
                results[domain] = ApplicationNotFound(domain)
            else:
                results[domain] = cast(Application, app_or_evt)

    if needed:
        from . import components #pylint: disable=import-outside-toplevel
        #TODO: applications is not implemented
        applications = await lightme.async_add_executor_job(
            _resolve_application_from_root, lightme, components, list(needed)
        )
        for domain, event in needed.items():
            application = applications.get(domain)
            if not application:
                cache.pop(domain)
                results[domain] = ApplicationNotFound(domain)
            elif isinstance(application, Exception):
                cache.pop(domain)
                exception_evt = ApplicationNotFound(domain)
                exception_evt.__cause__ = application
                results[domain] = exception_evt
            else:
                results[domain] = cache[domain] = application
            event.set()

    return results

def _async_mount_config_dir(lightme: LightMe) -> bool:
    """Mount configuration directory in order to load custom_component."""

    if lightme.config.config_dir is None:
        return False
    if lightme.config.config_dir not in sys.path:
        sys.path.insert(0, lightme.config.config_dir)
    return True
