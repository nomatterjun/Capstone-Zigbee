"""Light Me moment sensor."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)

class MomentSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, id):
        super().__init__(coordinator)

        self.id = id
        self.name: str | None = None
    
    @property
    def unique_id(self) -> str:
        """Return unique entity ID."""
        entity_id = cv.entity_id('{}.{}_{}'.format(Platform.SENSOR, DOMAIN, self.id))
        return entity_id

    @property
    def name(self) -> str:
        """Return name of moment sensor."""
        if self.name is None:
            self.name = 'Moment Sensor'
        else:
            return self.name
