import subprocess
from PIL import Image
import time
import io

# --- colors
YELLOW = (255, 216, 0) # loaded bar + continue button
WHITE = (255, 255, 255) # login error + resource recover click
GRAY = (49, 49, 49) # unloaded bar
BLACK = (0, 0, 0) # frozen
RED = (112, 14, 14) # confirm resource recover
LIGHT_GRAY = (85, 85, 85) # confirm login

# --- positions
CONTINUE = (959, 983) # yellow start icon
BAR = (1918, 1042) # loading bar
LOGIN = (959, 723) # login error/success
CACHE = (203, 74) # cache
RECOVER = (612, 577) # resource recover
CONFIRM = (1879, 773) # confirm resource recover

# --- arknights 
PACKAGE = 'com.YoStarEN.Arknights'

# --- function
# get color of coordinates on the emulator
def get_screen(position):
    raw = subprocess.check_output(['adb', 'exec-out', 'screencap', '-p'])
    img = Image.open(io.BytesIO(raw))
    return img.getpixel(position)

# check if current color match the target
def color_check(color_source, color_target, n):
    color_min = [x-5*n for x in color_target]
    color_max = [x+5*n for x in color_target]
    return all(
        mn <= c <= mx
        for c, mn, mx in zip(color_source, color_min, color_max)
    )

# click on the screen
def click(p):
    subprocess.run(['adb', 'shell', 'input', 'tap', str(p[0]), str(p[1])], check=True)
    time.sleep(0.5)

# click when colors match
def check(position, color_target, t=0, loop=False, color_limit=1, timeout=None):
    start = time.monotonic()
    while True:
        val = get_screen(position)
        if color_check(val, color_target, color_limit):
            click(position)
            return True
        
        if not loop:
            return False
        
        if timeout is not None and time.monotonic() - start > timeout:
            return False
        
        time.sleep(t)

# work loop
count = 0
while count < 3:
    # start Arknights
    time.sleep(5)
    check(CONTINUE, YELLOW, t=4, loop=True)
    time.sleep(12)
    # check login
    if check(LOGIN, LIGHT_GRAY):
        count = 3
        time.sleep(20)
        break
    else:
        check(LOGIN, WHITE)
        count+=1
        time.sleep(15)
    # freeze check
    if check(BAR, BLACK, t=3, loop=True, timeout=16):
        time.sleep(8)
        if check(BAR, BLACK):
            subprocess.run(['adb', 'shell', 'am', 'force-stop', PACKAGE], check=True)
            time.sleep(2)
            subprocess.run(['adb', 'shell', 'monkey', '-p', PACKAGE, '-c', 'android.intent.category.LAUNCHER', '1'], check=True)
            time.sleep(20)
    # recover resources
    time.sleep(10)
    click(CACHE)
    time.sleep(1)
    if not check(RECOVER, WHITE):
        count = 3
        break
    time.sleep(1)
    if not check(CONFIRM, RED, color_limit=2):
        count = 3
        break