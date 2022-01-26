# RTM home assistant

This module displays the time for the next RTM bus inside home assistant.


## Install

### HACS (recommended)

You can install this custom component using [HACS](https://hacs.xyz/) by adding a custom repository.

### Manual install

Copy this repository inside `config/custom_components/rtm`.

## Configuration

Add this to your `configuration.yaml`:

```yaml
sensor:
  - platform: rtm
    station_id: 1234  # bus station identifier (can be found by flashing the QR code at the bus stop)
```

This will create a sensor with the time for the next bus.
 
