import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinter"])
