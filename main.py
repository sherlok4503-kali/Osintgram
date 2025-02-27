#!/usr/bin/env python3

import os
import argparse
import sys
import signal
import time
import random

# Check if src directory exists
if not os.path.isdir("src"):
    print("Error: 'src' directory not found. Ensure you are in the correct directory.")
    sys.exit(1)

# Attempt to import required modules
try:
    from src.Osintgram import Osintgram
    from src import printcolors as pc
    from src import artwork
except ModuleNotFoundError as e:
    print(f"Error: {e}. Ensure the 'src' directory contains the required modules.")
    sys.exit(1)

# Detect Windows platform
is_windows = sys.platform.startswith("win")

# Handle readline imports
try:
    if is_windows:
        import pyreadline
    else:
        import readline
except ModuleNotFoundError:
    print("Error: Missing required module. Run: pip install -r requirements.txt")
    sys.exit(1)

# User-Agent Rotation Function
def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
    ]
    return random.choice(user_agents)

# Headers for request security
headers = {
    "User-Agent": get_random_user_agent(),
    "Accept-Language": "en-US,en;q=0.9",
}

# Delay Function to Avoid Detection
def apply_random_delay(min_time=5, max_time=15):
    delay = random.randint(min_time, max_time)
    print(f"Applying random delay: {delay} seconds to avoid detection...")
    time.sleep(delay)

def printlogo():
    pc.printout(artwork.ascii_art, pc.YELLOW)
    pc.printout("\nVersion 1.2 - Advanced OSINT Tool\n\n", pc.YELLOW)
    pc.printout("Type 'list' to show all allowed commands\n")
    pc.printout("Type 'FILE=y' to save results to files\n")
    pc.printout("Type 'JSON=y' to export results to JSON\n")

def cmdlist():
    commands = [
        ("FILE=y/n", "Enable/disable output to a file"),
        ("JSON=y/n", "Enable/disable export to JSON"),
        ("addrs", "Get all registered addresses by target photos"),
        ("followers", "Get target followers"),
        ("followings", "Get users followed by target"),
        ("info", "Get target info"),
        ("likes", "Get total likes of target's posts"),
        ("stories", "Download target's stories"),
        ("target", "Set new target"),
    ]
    for cmd, desc in commands:
        pc.printout(f"{cmd}\t\t{desc}\n")

def signal_handler(sig, frame):
    pc.printout("\nGoodbye!\n", pc.RED)
    sys.exit(0)

def _quit():
    pc.printout("Goodbye!\n", pc.RED)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if is_windows:
    pyreadline.Readline().parse_and_bind("tab: complete")
else:
    readline.parse_and_bind("tab: complete")

parser = argparse.ArgumentParser(description='Osintgram - Advanced Instagram OSINT Tool')
parser.add_argument('id', type=str, help='Username to analyze')
parser.add_argument('-C', '--cookies', help="Clear previous cookies", action="store_true")
parser.add_argument('-j', '--json', help="Save output as JSON", action='store_true')
parser.add_argument('-f', '--file', help="Save output in a file", action='store_true')
parser.add_argument('-c', '--command', help="Run single command mode", action='store')
parser.add_argument('-o', '--output', help="Where to store photos", action='store')

args = parser.parse_args()

# Ensure credentials.ini exists
credentials_path = "config/credentials.ini"
if not os.path.isfile(credentials_path):
    print("Warning: 'credentials.ini' file missing. Creating a blank template.")
    os.makedirs("config", exist_ok=True)
    with open(credentials_path, "w") as f:
        f.write("[CREDENTIALS]\nusername =\npassword =\n")
    print(f"Edit '{credentials_path}' and add your Instagram credentials.")

# Applying login delay
apply_random_delay()

# Initialize Osintgram with error handling
try:
    api = Osintgram(args.id, file=args.file, json=args.json, command=args.command, output=args.output, cookies=args.cookies)
except AttributeError as e:
    print(f"Error: {e}. Ensure Osintgram methods exist and match expected parameters.")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing Osintgram: {e}")
    sys.exit(1)

commands = {
    'list': cmdlist,
    'help': cmdlist,
    'quit': _quit,
    'exit': _quit,
}

if hasattr(api, "get_followers"):
    commands["followers"] = api.get_followers
if hasattr(api, "get_followings"):
    commands["followings"] = api.get_followings
if hasattr(api, "get_user_info"):
    commands["info"] = api.get_user_info
if hasattr(api, "get_total_likes"):
    commands["likes"] = api.get_total_likes
if hasattr(api, "get_user_stories"):
    commands["stories"] = api.get_user_stories
if hasattr(api, "change_target"):
    commands["target"] = api.change_target

if not args.command:
    printlogo()

while True:
    if args.command:
        cmd = args.command
    else:
        signal.signal(signal.SIGINT, signal_handler)
        pc.printout("Run a command: ", pc.YELLOW)
        cmd = input().strip()

    apply_random_delay(3, 10)

    _cmd = commands.get(cmd)

    if _cmd:
        try:
            _cmd()
        except Exception as e:
            print(f"Error executing command: {e}")
    elif cmd == "FILE=y":
        api.set_write_file(True)
    elif cmd == "FILE=n":
        api.set_write_file(False)
    elif cmd == "JSON=y":
        api.set_json_dump(True)
    elif cmd == "JSON=n":
        api.set_json_dump(False)
    elif cmd == "":
        continue
    else:
        pc.printout("Unknown command\n", pc.RED)

    if args.command:
        break
