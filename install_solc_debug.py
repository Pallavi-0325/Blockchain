from solcx import install_solc, get_installed_solc_versions

print("Checking installed versions...")
print(get_installed_solc_versions())

print("Attempting to install solc 0.8.0...")
try:
    install_solc('0.8.0')
    print("Success! Installed 0.8.0.")
except Exception as e:
    print(f"Failed to install: {e}")
    import traceback
    traceback.print_exc()

print("Verifying installation...")
print(get_installed_solc_versions())
