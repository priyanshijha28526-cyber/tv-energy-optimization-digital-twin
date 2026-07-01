import numpy as np
from scipy.interpolate import interp1d

# LED efficiency data

led_duty = np.array([
    0.02,0.05,0.10,0.20,
    0.40,0.60,0.80,1.00
])

led_eff = np.array([
    0.65,0.78,0.86,0.90,
    0.92,0.93,0.935,0.935
])

led_curve = interp1d(
    led_duty,
    led_eff,
    kind="linear",
    fill_value="extrapolate"
)

# SMPS efficiency data

smps_load = np.array([
    0.02,0.05,0.10,0.20,
    0.30,0.40,0.60,0.80,1.00
])

smps_eff = np.array([
    0.70,0.785,0.81,0.815,
    0.82,0.82,0.815,0.81,0.808
])

smps_curve = interp1d(
    smps_load,
    smps_eff,
    kind="linear",
    fill_value="extrapolate"
)

def tv_subsystem_power(
    brightness_pct,
    volume_pct,
    wifi_on=True
):
    BACKLIGHT_MAX = 55
    MAINBOARD_BASE = 15
    WIFI_POWER = 3
    AUDIO_MAX = 7
    MISC_POWER = 5

    backlight_power = (
        brightness_pct/100
    ) * BACKLIGHT_MAX

    audio_power = (
        volume_pct/100
    ) * AUDIO_MAX

    mainboard_power = MAINBOARD_BASE

    if wifi_on:
        mainboard_power += WIFI_POWER

    total = (
        backlight_power
        + audio_power
        + mainboard_power
        + MISC_POWER
    )

    return {
        "Backlight":backlight_power,
        "Audio":audio_power,
        "MainBoard":mainboard_power,
        "Misc":MISC_POWER,
        "Total":total
    }

def wall_power(
    brightness_pct,
    volume_pct,
    wifi_on=True,
    smps_max_load_W=85
):

    subsystems = tv_subsystem_power(
        brightness_pct,
        volume_pct,
        wifi_on
    )

    backlight_power = subsystems["Backlight"]

    duty_cycle = brightness_pct/100

    if backlight_power <= 0:

        eta_led = 0
        led_input_power = 0

    else:

        eta_led = float(
            led_curve(duty_cycle)
        )

        led_input_power = (
            backlight_power
            / eta_led
        )

    non_led_load = (
        subsystems["Audio"]
        + subsystems["MainBoard"]
        + subsystems["Misc"]
    )

    smps_output_power = (
        led_input_power
        + non_led_load
    )

    load_fraction = (
        smps_output_power
        / smps_max_load_W
    )

    load_fraction = np.clip(
        load_fraction,
        0.02,
        1.0
    )

    eta_smps = float(
        smps_curve(load_fraction)
    )

    wall_power_W = (
        smps_output_power
        / eta_smps
    )

    return {
        "WallPower":wall_power_W,
        "SMPS_Eff":eta_smps,
        "LED_Eff":eta_led,
        "Subsystems":subsystems
    }