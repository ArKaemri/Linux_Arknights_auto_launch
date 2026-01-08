#!/bin/bash
set -e
ulimit -n 1048576

# values
MAA_PATH="$HOME/Personal/maa" # change MAA executable path
PYTHON_FILE_PATH="$HOME/Scripts/arknights" # change python file path
ANDROID_NAME="Arknights" # change emulator name
PACKAGE="com.YoStarEN.Arknights"

# optional maa task
MAA_TASK_FILE="$1"

# launch emulator
setsid "$HOME/Android/Sdk/emulator/emulator" \
-avd "$ANDROID_NAME" \
-no-snapshot \
-no-snapshot-save \
-no-boot-anim \
>/dev/null 2>&1 &

# wait for emulator
adb wait-for-device
echo "Waiting for boot..."
while [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" != "1" ]; do
    sleep 1
done

sleep 5

# launch arknights
adb shell "monkey -p $PACKAGE -c android.intent.category.LAUNCHER 1"

# launch python
cd "$PYTHON_FILE_PATH"
source .venv/bin/activate
python3 arknights.py

# launch maa task if given
if [ -n "$MAA_TASK_FILE" ]; then
    cd "$MAA_PATH"
    ./maa run "$MAA_TASK_FILE"
fi