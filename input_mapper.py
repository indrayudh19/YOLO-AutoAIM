import pygame
import time
import math

import windows_input


# ============================================================
# CONFIGURATION
# ============================================================

# Stick deadzone.
# Increase if the character/camera moves when the sticks are
# physically centered.
DEADZONE = 0.18


# Right-stick mouse sensitivity.
# Increase = faster camera movement.
MOUSE_SENSITIVITY = 12.0


# Response curve.
# 1.0 = linear
# >1.0 = more precise around center
MOUSE_RESPONSE = 1.5


# Trigger threshold.
# Xbox triggers normally report:
#
# released = approximately -1
# pressed  = approximately +1
#
# This converts them into a 0.0 - 1.0 range.
TRIGGER_THRESHOLD = 0.50


# ============================================================
# D-PAD WEAPON MAPPING
# ============================================================
#
# Change these later if you want a different weapon layout.
#
# Current temporary mapping:
#
# UP    -> 1
# DOWN  -> 2
# LEFT  -> 3
# RIGHT -> 4
#

DPAD_WEAPONS = {
    "UP": "1",
    "DOWN": "2",
    "LEFT": "3",
    "RIGHT": "4",
}


# ============================================================
# CONTROLLER BUTTONS
# ============================================================

BUTTONS = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "LB",
    5: "RB",
    8: "LEFT STICK CLICK",
    9: "RIGHT STICK CLICK",
}


# ============================================================
# BUTTON → KEY MAPPING
# ============================================================

BUTTON_TO_KEY = {

    # Xbox A → Space
    0: "SPACE",

    # Xbox B → R
    1: "R",

    # Xbox X → C
    2: "C",

    # Xbox Y → E
    3: "E",

    # Xbox RB → Shift
    5: "SHIFT",
}


# ============================================================
# AXIS DEFINITIONS
# ============================================================

LEFT_X = 0
LEFT_Y = 1

RIGHT_X = 2
RIGHT_Y = 3

LT_AXIS = 4
RT_AXIS = 5


# ============================================================
# STATE
# ============================================================

held_keys = set()

left_mouse_held = False
right_mouse_held = False


# ============================================================
# DEADZONE
# ============================================================

def apply_deadzone(value):

    if abs(value) < DEADZONE:
        return 0.0

    sign = 1 if value > 0 else -1

    magnitude = (abs(value) - DEADZONE) / (1.0 - DEADZONE)

    return sign * magnitude


# ============================================================
# TRIGGER NORMALIZATION
# ============================================================

def normalize_trigger(value):

    # Raw Xbox trigger:
    #
    # -1 = released
    # +1 = fully pressed

    normalized = (value + 1.0) / 2.0

    normalized = max(0.0, min(1.0, normalized))

    return normalized


# ============================================================
# KEY STATE MANAGEMENT
# ============================================================

def set_key_state(key, should_be_down):

    global held_keys

    if should_be_down:

        if key not in held_keys:

            windows_input.key_down(key)
            held_keys.add(key)

    else:

        if key in held_keys:

            windows_input.key_up(key)
            held_keys.remove(key)


# ============================================================
# RELEASE EVERYTHING
# ============================================================

def release_all():

    global held_keys
    global left_mouse_held
    global right_mouse_held

    # Release keyboard keys

    for key in list(held_keys):

        try:
            windows_input.key_up(key)
        except Exception:
            pass

    held_keys.clear()

    # Release mouse buttons

    if left_mouse_held:

        try:
            windows_input.left_mouse_up()
        except Exception:
            pass

        left_mouse_held = False

    if right_mouse_held:

        try:
            windows_input.right_mouse_up()
        except Exception:
            pass

        right_mouse_held = False


# ============================================================
# MOVEMENT
# ============================================================

def update_movement(joystick):

    x = apply_deadzone(
        joystick.get_axis(LEFT_X)
    )

    y = apply_deadzone(
        joystick.get_axis(LEFT_Y)
    )

    # Xbox/Pygame:
    #
    # stick up    = negative Y
    # stick down  = positive Y

    set_key_state("A", x < -DEADZONE)
    set_key_state("D", x > DEADZONE)

    set_key_state("W", y < -DEADZONE)
    set_key_state("S", y > DEADZONE)


# ============================================================
# CAMERA
# ============================================================

def update_camera(joystick):

    x = apply_deadzone(
        joystick.get_axis(RIGHT_X)
    )

    y = apply_deadzone(
        joystick.get_axis(RIGHT_Y)
    )

    if x == 0 and y == 0:
        return

    # Response curve
    #
    # This makes small stick movements more precise while
    # retaining faster movement when the stick is pushed far.

    x = math.copysign(
        abs(x) ** MOUSE_RESPONSE,
        x
    )

    y = math.copysign(
        abs(y) ** MOUSE_RESPONSE,
        y
    )

    dx = x * MOUSE_SENSITIVITY
    dy = y * MOUSE_SENSITIVITY

    windows_input.move_mouse(
        int(dx),
        int(dy)
    )


# ============================================================
# BUTTON HANDLING
# ============================================================

def handle_button_down(button):

    name = BUTTONS.get(button, f"BUTTON {button}")

    print(f"[BUTTON] {name} PRESSED")

    # Ignore buttons without mappings
    if button not in BUTTON_TO_KEY:
        return

    key = BUTTON_TO_KEY[button]

    # A/B/X/Y are individual actions.
    # Press and immediately release.
    #
    # RB is different because it is Shift and should be held.

    if button == 5:

        set_key_state("SHIFT", True)

    else:

        windows_input.press_key(key)


def handle_button_up(button):

    name = BUTTONS.get(button, f"BUTTON {button}")

    print(f"[BUTTON] {name} RELEASED")

    # RB / Shift must remain held while RB is held.

    if button == 5:

        set_key_state("SHIFT", False)


# ============================================================
# TRIGGERS
# ============================================================

def update_triggers(joystick):

    global left_mouse_held
    global right_mouse_held

    lt_raw = joystick.get_axis(LT_AXIS)
    rt_raw = joystick.get_axis(RT_AXIS)

    lt = normalize_trigger(lt_raw)
    rt = normalize_trigger(rt_raw)

    # --------------------------------------------------------
    # LT → RIGHT MOUSE → SLOWDOWN
    # --------------------------------------------------------

    lt_pressed = lt >= TRIGGER_THRESHOLD

    if lt_pressed and not right_mouse_held:

        windows_input.right_mouse_down()
        right_mouse_held = True

        print("[TRIGGER] LT → RIGHT MOUSE DOWN")

    elif not lt_pressed and right_mouse_held:

        windows_input.right_mouse_up()
        right_mouse_held = False

        print("[TRIGGER] LT → RIGHT MOUSE UP")

    # --------------------------------------------------------
    # RT → LEFT MOUSE → SHOOT
    # --------------------------------------------------------

    rt_pressed = rt >= TRIGGER_THRESHOLD

    if rt_pressed and not left_mouse_held:

        windows_input.left_mouse_down()
        left_mouse_held = True

        print("[TRIGGER] RT → LEFT MOUSE DOWN")

    elif not rt_pressed and left_mouse_held:

        windows_input.left_mouse_up()
        left_mouse_held = False

        print("[TRIGGER] RT → LEFT MOUSE UP")


# ============================================================
# D-PAD
# ============================================================

previous_hat = (0, 0)


def handle_dpad(joystick):

    global previous_hat

    current_hat = joystick.get_hat(0)

    # Don't repeatedly fire the same weapon selection.

    if current_hat == previous_hat:
        return

    previous_hat = current_hat

    # --------------------------------------------------------
    # RELEASE
    # --------------------------------------------------------

    if current_hat == (0, 0):

        print("[D-PAD] RELEASED")
        return

    # --------------------------------------------------------
    # UP
    # --------------------------------------------------------

    if current_hat == (0, 1):

        key = DPAD_WEAPONS["UP"]

        print(f"[D-PAD] UP → Weapon {key}")
        windows_input.press_key(key)

    # --------------------------------------------------------
    # DOWN
    # --------------------------------------------------------

    elif current_hat == (0, -1):

        key = DPAD_WEAPONS["DOWN"]

        print(f"[D-PAD] DOWN → Weapon {key}")
        windows_input.press_key(key)

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    elif current_hat == (-1, 0):

        key = DPAD_WEAPONS["LEFT"]

        print(f"[D-PAD] LEFT → Weapon {key}")
        windows_input.press_key(key)

    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    elif current_hat == (1, 0):

        key = DPAD_WEAPONS["RIGHT"]

        print(f"[D-PAD] RIGHT → Weapon {key}")
        windows_input.press_key(key)


# ============================================================
# MAIN
# ============================================================

def main():

    global previous_hat

    pygame.init()
    pygame.joystick.init()

    print()
    print("=" * 60)
    print("XBOX CONTROLLER → WINDOWS INPUT MAPPER")
    print("=" * 60)

    # --------------------------------------------------------
    # CONTROLLER DETECTION
    # --------------------------------------------------------

    if pygame.joystick.get_count() == 0:

        print()
        print("ERROR: No controller detected.")
        print("Connect the Xbox controller and run the program again.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print()
    print(f"Controller: {joystick.get_name()}")

    print()
    print("CONTROLLER MAPPING")
    print("------------------")

    print("Left Stick  → WASD")
    print("Right Stick → Mouse")
    print("A           → SPACE")
    print("B           → R")
    print("X           → C")
    print("Y           → E")
    print("RB          → SHIFT")
    print("RT          → LEFT MOUSE")
    print("LT          → RIGHT MOUSE")
    print("D-Pad       → 1 / 2 / 3 / 4")

    print()
    print("Press CTRL+C to stop.")
    print("=" * 60)
    print()

    clock = pygame.time.Clock()

    running = True

    try:

        while running:

            # ------------------------------------------------
            # PYGAME EVENTS
            # ------------------------------------------------

            for event in pygame.event.get():

                # Controller button pressed

                if event.type == pygame.JOYBUTTONDOWN:

                    handle_button_down(
                        event.button
                    )

                # Controller button released

                elif event.type == pygame.JOYBUTTONUP:

                    handle_button_up(
                        event.button
                    )

                # Controller disconnected

                elif event.type == pygame.JOYDEVICEREMOVED:

                    print()
                    print("Controller disconnected.")

                    running = False

                # Controller connected

                elif event.type == pygame.JOYDEVICEADDED:

                    print("Controller connected.")

            # ------------------------------------------------
            # CONTINUOUS INPUT
            # ------------------------------------------------

            update_movement(joystick)

            update_camera(joystick)

            update_triggers(joystick)

            handle_dpad(joystick)

            # ------------------------------------------------
            # LIMIT LOOP
            # ------------------------------------------------

            clock.tick(120)

    except KeyboardInterrupt:

        print()
        print("Stopping mapper...")

    finally:

        print("Releasing all inputs...")

        release_all()

        pygame.quit()

        print("Mapper stopped safely.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()