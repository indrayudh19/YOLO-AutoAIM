import ctypes
from ctypes import wintypes


# ============================================================
# WINDOWS API
# ============================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


# Correct pointer-sized integer for 64-bit Windows
ULONG_PTR = ctypes.c_ulonglong


# ============================================================
# WINDOWS STRUCTURES
# ============================================================

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)

    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


# ============================================================
# INTERNAL SEND FUNCTION
# ============================================================

def _send_input(input_data):

    result = user32.SendInput(
        1,
        ctypes.byref(input_data),
        ctypes.sizeof(INPUT)
    )

    if result != 1:
        raise ctypes.WinError(ctypes.get_last_error())


# ============================================================
# KEYBOARD MAP
# ============================================================

KEYS = {

    # Movement
    "W": 0x57,
    "A": 0x41,
    "S": 0x53,
    "D": 0x44,

    # Actions
    "SPACE": 0x20,
    "C": 0x43,
    "E": 0x45,
    "R": 0x52,

    # Dodge
    "SHIFT": 0x10,

    # Weapon slots
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
}


# ============================================================
# KEYBOARD FUNCTIONS
# ============================================================

def key_down(key):

    key = key.upper()

    if key not in KEYS:
        raise ValueError(f"Unknown key: {key}")

    inp = INPUT()
    inp.type = INPUT_KEYBOARD

    inp.ki = KEYBDINPUT(
        wVk=KEYS[key],
        wScan=0,
        dwFlags=0,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def key_up(key):

    key = key.upper()

    if key not in KEYS:
        raise ValueError(f"Unknown key: {key}")

    inp = INPUT()
    inp.type = INPUT_KEYBOARD

    inp.ki = KEYBDINPUT(
        wVk=KEYS[key],
        wScan=0,
        dwFlags=KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def press_key(key):

    key_down(key)
    key_up(key)


# ============================================================
# MOUSE
# ============================================================

def move_mouse(dx, dy):

    if dx == 0 and dy == 0:
        return

    inp = INPUT()
    inp.type = INPUT_MOUSE

    inp.mi = MOUSEINPUT(
        dx=int(dx),
        dy=int(dy),
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def left_mouse_down():

    inp = INPUT()
    inp.type = INPUT_MOUSE

    inp.mi = MOUSEINPUT(
        dx=0,
        dy=0,
        mouseData=0,
        dwFlags=MOUSEEVENTF_LEFTDOWN,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def left_mouse_up():

    inp = INPUT()
    inp.type = INPUT_MOUSE

    inp.mi = MOUSEINPUT(
        dx=0,
        dy=0,
        mouseData=0,
        dwFlags=MOUSEEVENTF_LEFTUP,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def right_mouse_down():

    inp = INPUT()
    inp.type = INPUT_MOUSE

    inp.mi = MOUSEINPUT(
        dx=0,
        dy=0,
        mouseData=0,
        dwFlags=MOUSEEVENTF_RIGHTDOWN,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)


def right_mouse_up():

    inp = INPUT()
    inp.type = INPUT_MOUSE

    inp.mi = MOUSEINPUT(
        dx=0,
        dy=0,
        mouseData=0,
        dwFlags=MOUSEEVENTF_RIGHTUP,
        time=0,
        dwExtraInfo=0
    )

    _send_input(inp)