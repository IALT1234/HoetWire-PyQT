import platform

system = platform.system()
arch = platform.machine()

print(f"[DEBUG] Detected system: {system}")
print(f"[DEBUG] Detected architecture: {arch}")

# More robust Raspberry Pi check
IS_PI = system == 'Linux' and (arch.startswith('arm') or arch == 'aarch64')

print(f"[CONFIG] IS_PI = {IS_PI}")