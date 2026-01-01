import PyInstaller.__main__
import customtkinter
import os
import platform

# Determine the separator for --add-data based on the OS
# Windows uses ';', Linux/Unix uses ':'
system_os = platform.system()
if system_os == "Windows":
    separator = ";"
    print("Detected Windows. Using ';' separator.")
else:
    separator = ":"
    print(f"Detected {system_os}. Using ':' separator.")

# Get the installation directory of customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)
print(f"CustomTkinter found at: {ctk_path}")

# Construct the --add-data argument
add_data_arg = f"{ctk_path}{separator}customtkinter"

# Define PyInstaller arguments
pyinstaller_args = [
    'discord_rpc_gui.py',     # Your main script
    '--name=DiscordRPC',      # Name of the executable
    '--onefile',              # Create a single executable file
    '--noconsole',            # Don't show a terminal window when running
    f'--add-data={add_data_arg}', # Add CustomTkinter assets
    '--clean',                # Clean cache before building
]

print("Starting build with arguments:", pyinstaller_args)

# Run PyInstaller
PyInstaller.__main__.run(pyinstaller_args)
