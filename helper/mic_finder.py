import sounddevice as sd

print("🎤 Available audio input devices:\n")
for i, device in enumerate(sd.query_devices()):
    if device['max_input_channels'] > 0:
        print(f"{i}: {device['name']}")