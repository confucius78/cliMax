# Notice

This integration intends to help a user control multiple climate devices in a zone
by providing a single thermostat and control logic behind-the scenes that takes care
of setting the devices' thermostats. An example use-case is combining floor heating
with AC heating in winter time.

## Why?

The challenge with combining multiple climate devices in a single zone is that typically
one device will take all the actions while the second never kicks in due to its thermostat
reading outside the control limits. The climax coordinator avoids this by using other metrics
to track whether a climate device's action is needed.

In addition to this, the controller allows multiple sensor inputs to be provided which will
be combined and converted into a control signal for the actual device.

## What?

This repository contains multiple files, here is a overview:

File | Purpose
-- | --
`.devcontainer/*` | Used for development/testing with VSCODE, more info in the readme file in that dir.
`.github/ISSUE_TEMPLATE/feature_request.md` | Template for Feature Requests
`.github/ISSUE_TEMPLATE/issue.md` | Template for issues
`.vscode/tasks.json` | Tasks for the devcontainer.
`custom_components/integration_blueprint/translations/*` | [Translation files.](https://developers.home-assistant.io/docs/internationalization/custom_integration)
`custom_components/integration_blueprint/__init__.py` | The component file for the integration.
`custom_components/integration_blueprint/api.py` | This is a sample API client.
`custom_components/integration_blueprint/binary_sensor.py` | Binary sensor platform for the integration.
`custom_components/integration_blueprint/config_flow.py` | Config flow file, this adds the UI configuration possibilities.
`custom_components/integration_blueprint/const.py` | A file to hold shared variables/constants for the entire integration.
`custom_components/integration_blueprint/manifest.json` | A [manifest file](https://developers.home-assistant.io/docs/en/creating_integration_manifest.html) for Home Assistant.
`custom_components/integration_blueprint/sensor.py` | Sensor platform for the integration.
`custom_components/integration_blueprint/switch.py` | Switch sensor platform for the integration.
`tests/__init__.py` | Makes the `tests` folder a module.
`tests/conftest.py` | Global [fixtures](https://docs.pytest.org/en/stable/fixture.html) used in tests to [patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) functions.
`tests/test_api.py` | Tests for `custom_components/integration_blueprint/api.py`.
`tests/test_config_flow.py` | Tests for `custom_components/integration_blueprint/config_flow.py`.
`tests/test_init.py` | Tests for `custom_components/integration_blueprint/__init__.py`.
`tests/test_switch.py` | Tests for `custom_components/integration_blueprint/switch.py`.
`CONTRIBUTING.md` | Guidelines on how to contribute.
`example.png` | Screenshot that demonstrate how it might look in the UI.
`info.md` | An example on a info file (used by [hacs][hacs]).
`LICENSE` | The license file for the project.
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions.
`requirements.txt` | Python packages used by this integration.
`requirements_dev.txt` | Python packages used to provide [IntelliSense](https://code.visualstudio.com/docs/editor/intellisense)/code hints during development of this integration, typically includes packages in `requirements.txt` but may include additional packages
`requirements_test.txt` | Python packages required to run the tests for this integration, typically includes packages in `requirements_dev.txt` but may include additional packages

## How?

If you want to use all the potential and features of this blueprint template you
should use Visual Studio Code to develop in a container. In this container you
will have all the tools to ease your python development and a dedicated Home
Assistant core instance to run your integration. See `.devcontainer/README.md` for more information.

If you need to work on the python library in parallel of this integration
(`sampleclient` in this example) there are different options. The following one seems
easy to implement:

- Create a dedicated branch for your python library on a public git repository (example: branch
`dev` on `https://github.com/ludeeus/sampleclient`)
- Update in the `manifest.json` file the `requirements` key to point on your development branch
( example: `"requirements": ["git+https://github.com/ludeeus/sampleclient.git@dev#devp==0.0.1beta1"]`)
- Each time you need to make a modification to your python library, push it to your
development branch and increase the number of the python library version in `manifest.json` file
to ensure Home Assistant update the code of the python library. (example `"requirements": ["git+https://...==0.0.1beta2"]`).


***
README content if this was a published component:
***

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to coordinate multiple climate devices._

**This component will set up the following platforms.**

Platform | Description
`climax` | Main coordinator.
`climate` | Control climate device.
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from API.
`switch` | Switch something `True` or `False`.

![example][exampleimg]

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Blueprint".

{% endif %}


## Configuration is done in the UI

<!---->

***

[climax]: https://github.com/custom-components/climax
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/integration_blueprint.svg?style=for-the-badge
[commits]: https://github.com/custom-components/integration_blueprint/commits/master
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/confucius78/cliMax/blob/master/LICENSE
[license-shield]: https://img.shields.io/github/license/custom-components/integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/custom-components/integration_blueprint.svg?style=for-the-badge
[releases]: https://github.com/custom-components/integration_blueprint/releases
[user_profile]: https://github.com/ludeeus
