import configparser
import sys
import os

# Attempt to import printcolors, fallback to print if missing
try:
    from src import printcolors as pc
    def printout(message, color=None):
        pc.printout(message, color)
except ImportError:
    def printout(message, color=None):
        print(message)

# Ensure config directory exists
config_dir = "config"
credentials_file = os.path.join(config_dir, "credentials.ini")

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Create default credentials.ini if missing
if not os.path.isfile(credentials_file):
    printout('Warning: "credentials.ini" file missing. Creating a blank template.', None)
    with open(credentials_file, "w") as f:
        f.write("[Credentials]\nusername =\npassword =\n")
    printout(f'Edit "{credentials_file}" and add your Instagram credentials.', None)

# Read config file safely
config = configparser.ConfigParser(interpolation=None)
config.read(credentials_file)

def getUsername():
    try:
        username = config.get("Credentials", "username", fallback="")
        if not username:
            printout('Error: "username" field cannot be blank in "config/credentials.ini"', "RED")
            sys.exit(0)
        return username
    except KeyError:
        printout('Error: missing "username" field in "config/credentials.ini"', "RED")
        sys.exit(0)

def getPassword():
    try:
        password = config.get("Credentials", "password", fallback="")
        if not password:
            printout('Error: "password" field cannot be blank in "config/credentials.ini"', "RED")
            sys.exit(0)
        return password
    except KeyError:
        printout('Error: missing "password" field in "config/credentials.ini"', "RED")
        sys.exit(0)
