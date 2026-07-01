import numpy as np

def recommended_backlight(
    ambient_light,
    content_brightness,
    eco_mode=False
):

    brightness = (
        0.55 * ambient_light
        + 0.45 * content_brightness
    )

    brightness = np.clip(
    brightness,
    40,
    100
)

    if eco_mode:
        brightness *= 0.9

    brightness = np.clip(
    brightness,
    40,
    100
)

    return brightness