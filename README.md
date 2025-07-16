# AmbiHue

[![Run SuperLinter](https://github.com/klimak000/ambihue/actions/workflows/superlinter.yml/badge.svg)](https://github.com/klimak000/ambihue/actions/workflows/superlinter.yml)
[![Build Docker Image](https://github.com/klimak000/ambihue/actions/workflows/docker_build.yml/badge.svg)](https://github.com/klimak000/ambihue/actions/workflows/docker_build.yml)

Program restores connection between Philips Ambilight TVs and the Hue Bridge by reading Ambilight data from the TV and forwarding it to Hue via the Entertainment Area API.

The Hue Entertainment Area provides low-latency color updates, offering significantly faster response times compared to standard light control via the Hue API.

**It is possilbe to get 15 updates per second!**

![preview](.github/images/preview.png)


```mermaid
classDiagram
    class TV {
        ambilight data
        share data via TV API
    }

    class AmbiHue {
        read TV data
        know light's positions
        calculate lights colors
        send to HueBridge
    }

    class HueBridge {
        sync via entertainment area
        low-latency
    }

    TV --> AmbiHue : ambilight data
    AmbiHue --> HueBridge : light color updates

```

## Setup user configuration

1. Copy config:

   ```bash
   cp userconfig.example.yaml userconfig.yaml
   ```

1. Install `ambihue` repository

   Activate virtual env

   ```bash
   pip3 install -r requirements.txt
   pip3 install .
   ```

### Setup Ambilight TV

1. Setup IP, protocol, prot and API version.

1. In case of problem use [`pylips` config discover feature](https://github.com/eslavnov/pylips/tree/master?tab=readme-ov-file#new-users)

1. Verify connection by calling ambihue

    ```bash
    ./ambihue.py --verify tv --loglevel DEBUG
    ```

### Setup Hue Entertainment

1. Create Entertainment area in Philips app. [See official tutorial](https://www.youtube.com/watch?v=OlXapdkedus)

1. Get your bridge access data

    ```bash
    ./ambihue.py --discover_hue --loglevel DEBUG
    ```

   More information on [`hue-entertainment-pykit` repository readme.](https://github.com/hrdasdominik/hue-entertainment-pykit?tab=readme-ov-file#discovery-optional)

1. Use printed values to fill config `hue_entertainment_group` config data
1. Verify connection by calling ambihue

    ```bash
    ./ambihue.py --verify hue --loglevel DEBUG
    ```

   One of your lights should be red now.

### Setup Light Position

1. Add light configuration:

    ```yaml
    your_light_name:
        id: 2  # light number from Hue Entertainment - manual adjustment
        positions: [5,6,7]  # indexes of color positions used to calculate the average color
    ```

    Positions index `[1-16]` table:

    ```text
    [4] 0Top  [5]1T  [6]2T  [7]3T  [8]4T  [9]5T  [10]6T  [11]7T  [12] 8Top
    [3] 3Left  ↗    →          →        →       →       →      ↘ [13] 0Right
    [2] 2Left  ↑                                               ↓ [14] 1Right
    [1] 1Left  ↑                                               ↓ [15] 2Right
    [0] 0Left  ↑                                               ↓ [16] 3Right
    ```

    Example of config:

    ```yaml
    lights_setup:
        left:
            id: 3
            positions: [2, 3, 4]
        right:
            id: 2
            positions: [12]
    ```

1. Use [this video to test colors](https://youtu.be/8u4UzzJZAUg?t=66)
1. To verify  config run ambihue

    ```bash
    ./ambihue.py --loglevel DEBUG
    ```

## Home Assistance Usage

### Via UI

1. [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fklimak000%2Fambihue)
1. Navigate to HA Addon and click `AmbiHue`

    ![preview](.github/images/ha_store.png)

1. Install addon and navigate to `Configuration` card

1. Click `Options` 3 dots and click `Edit in YAML`

1. Copy `userconfig.yaml` from setup stage


### For Developers

1. Upload code with configured `userconfig.yaml`:

   ```bash
   rsync -r ../ambihue root@111.222.333.444:/addons --stats
   ```

1. Use installed addon as local addon by [following official guide](https://developers.home-assistant.io/docs/add-ons/tutorial#step-2-installing-and-testing-your-add-on)

1. Every upload requires `config.yaml`[`version`] update to make changes visible for HA.

## Files structure

- `.github` - GitHub and linters data
- `.gitignore`
- `build.yaml` - additional build options Home Assistance addon
- `config.yaml` - Home Assistance addon config
- `Dockerfile` - Home Assistance image
- `pyproject.toml` - Python project config
- `requirements.txt` - Python packages
- `userconfig.example.yaml` - copy, rename to `userconfig.yaml`, fill up
- `repository.yaml` - Home Assistance addon repository config

## Validate code changes

Run script

```bash
./.github/verify_code.py
```

### Test building for others platform

   ```bash
   docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
   docker build --progress=plain --debug --platform linux/arm64/v8 -t ambihue_test_arm8 .
   docker build --progress=plain --debug --platform linux/arm/v7 -t ambihue_test_arm7 .
   ```
