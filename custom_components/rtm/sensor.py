from datetime import timedelta, datetime
import logging
import traceback

from custom_components.rtm.rtm import RTM
import voluptuous as conf

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, STATE_CLASS_TOTAL_INCREASING
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_time_interval, call_later

_LOGGER = logging.getLogger(__name__)

# INTERVAL CONSTANTS
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
FIRST_RUN_INTERVAL    = 5

# LABEL CONSTANTS
HA_RTM_NOM_ARRET_STR      = 'RTM Nom arrêt'
HA_RTM_NUMERO_LIGNE_STR   = 'RTM Numéro ligne'
HA_RTM_HEURE_PASSAGE_STR  = 'RTM Heure passage'
HA_RTM_PASSAGE_REEL_STR   = 'RTM Passage réel'
HA_RTM_TERMINUS_LIGNE_STR = 'Terminus ligne'
CONF_RTM_STATION          = 'station_id'

# Config for variables verification
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    conf.Required(CONF_RTM_STATION): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Configure the platform and add the RTM sensor."""

    _LOGGER.debug('Initializing RTM platform...')

    try:
        nom_pt_reseau = config[CONF_RTM_STATION]

        details = RTMStationDetail(hass, nom_pt_reseau)
        add_entities(details.sensors, True)

        _LOGGER.debug('RTM platform initialization has completed successfully')
    except BaseException:
        _LOGGER.error('RTM platform initialization has failed with exception : {0}'.format(traceback.format_exc()))


class RTMStationDetail:
    """Representation of a RTM station details."""

    def __init__(self, hass, nom_pt_reseau):
        """Initialise the RTM account."""
        self._nom_pt_reseau = nom_pt_reseau
        self.sensors = []

        # call api first time in FIRST_RUN_INTERVAL
        call_later(hass, FIRST_RUN_INTERVAL, self.update_rtm_data)

        # Init sensors with empty value
        self.sensors.append(RTMSensor(HA_RTM_NOM_ARRET_STR))
        self.sensors.append(RTMSensor(HA_RTM_NUMERO_LIGNE_STR))
        self.sensors.append(RTMSensor(HA_RTM_HEURE_PASSAGE_STR))
        self.sensors.append(RTMSensor(HA_RTM_PASSAGE_REEL_STR))
        self.sensors.append(RTMSensor(HA_RTM_TERMINUS_LIGNE_STR))

        # call api every DEFAULT_SCAN_INTERVAL
        track_time_interval(hass, self.update_rtm_data, DEFAULT_SCAN_INTERVAL)

    def update_rtm_data(self, event_time):
        """Fetch new state data for the sensor."""
        _LOGGER.debug('Querying RTM library for new data...')

        try:
            # Get full month data
            station_details = RTM()
            com_lieu, nom_ligne_cial, heure_passage_reel, passage_reel, destination = station_details.get_station_details(self._nom_pt_reseau)

            # Update sensors value
            for sensor in self.sensors:
                if sensor.name == HA_RTM_NOM_ARRET_STR:
                    sensor.set_data(com_lieu, 'mdi:bus-stop-uncovered')
                elif sensor.name == HA_RTM_NUMERO_LIGNE_STR:
                    sensor.set_data(nom_ligne_cial, 'mdi:bus')
                elif sensor.name == HA_RTM_HEURE_PASSAGE_STR:
                    sensor.set_data(heure_passage_reel, 'mdi:clock-outline')
                elif sensor.name == HA_RTM_PASSAGE_REEL_STR:
                    sensor.set_data(passage_reel, 'mdi:flag')
                elif sensor.name == HA_RTM_TERMINUS_LIGNE_STR:
                    sensor.set_data(destination, 'mdi:bus-stop-uncovered')

                sensor.async_schedule_update_ha_state(True)

                _LOGGER.debug('RTM data update')
        except BaseException:
            _LOGGER.error('Failed to query RTM webapi with exception : {0}'.format(traceback.format_exc()))

    @property
    def username(self):
        """Return the username."""
        return self._username


class RTMSensor(SensorEntity):
    """Representation of a sensor entity for RTM."""

    def __init__(self, name, icon):
        """Initialize the sensor."""
        self._name = name
        self._icon = icon
        self._unit = None
        self._measure = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._measure

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    def set_data(self, measure):
        """Update sensor data"""
        self._measure = measure
