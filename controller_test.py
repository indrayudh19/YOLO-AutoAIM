import pygame
import sys
import time


# ============================================================
# Xbox Controller Diagnostic Tool
# ============================================================

pygame.init()
pygame.joystick.init()


def list_controllers():
    """Display all controllers currently connected."""

    count = pygame.joystick.get_count()

    if count == 0:
        print("\nNo controller detected.")
        return False

    print(f"\nDetected {count} controller(s):")

    for i in range(count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        print(f"\nController {i}")
        print(f"  Name:    {joystick.get_name()}")
        print(f"  Axes:    {joystick.get_numaxes()}")
        print(f"  Buttons: {joystick.get_numbuttons()}")
        print(f"  Hats:    {joystick.get_numhats()}")

    return True


# ------------------------------------------------------------
# Detect controller
# ------------------------------------------------------------

if not list_controllers():
    print("\nConnect your Xbox controller through USB.")
    print("Then run this program again.")
    pygame.quit()
    sys.exit()


# ------------------------------------------------------------
# Use the first controller
# ------------------------------------------------------------

controller = pygame.joystick.Joystick(0)
controller.init()

print("\n" + "=" * 60)
print("CONTROLLER CONNECTED")
print("=" * 60)

print(f"Name: {controller.get_name()}")
print(f"Axes: {controller.get_numaxes()}")
print(f"Buttons: {controller.get_numbuttons()}")
print(f"Hats: {controller.get_numhats()}")

print("\nMove the sticks and press buttons.")
print("Press CTRL+C to exit.")
print("=" * 60)


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def clean_axis(value):
    """
    Small values around zero are usually controller noise.
    Ignore them so the output is easier to read.
    """

    if abs(value) < 0.10:
        return 0.0

    return round(value, 3)


# ------------------------------------------------------------
# Main controller loop
# ------------------------------------------------------------

try:

    while True:

        for event in pygame.event.get():

            # ------------------------------------------------
            # Button pressed
            # ------------------------------------------------

            if event.type == pygame.JOYBUTTONDOWN:

                print(
                    f"[BUTTON DOWN] "
                    f"Button {event.button}"
                )

            # ------------------------------------------------
            # Button released
            # ------------------------------------------------

            elif event.type == pygame.JOYBUTTONUP:

                print(
                    f"[BUTTON UP] "
                    f"Button {event.button}"
                )

            # ------------------------------------------------
            # Analog stick / trigger movement
            # ------------------------------------------------

            elif event.type == pygame.JOYAXISMOTION:

                value = clean_axis(event.value)

                if value != 0.0:

                    print(
                        f"[AXIS] "
                        f"Axis {event.axis}: {value}"
                    )

            # ------------------------------------------------
            # D-pad
            # ------------------------------------------------

            elif event.type == pygame.JOYHATMOTION:

                print(
                    f"[D-PAD] "
                    f"Hat {event.hat}: {event.value}"
                )

            # ------------------------------------------------
            # Controller connected
            # ------------------------------------------------

            elif event.type == pygame.JOYDEVICEADDED:

                print("\n[CONTROLLER CONNECTED]")

            # ------------------------------------------------
            # Controller disconnected
            # ------------------------------------------------

            elif event.type == pygame.JOYDEVICEREMOVED:

                print("\n[CONTROLLER DISCONNECTED]")

        time.sleep(0.01)


except KeyboardInterrupt:

    print("\n\nExiting controller test...")

finally:

    pygame.quit()
    print("Controller system closed.")