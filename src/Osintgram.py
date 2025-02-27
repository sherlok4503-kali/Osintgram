import datetime
import json
import sys
import urllib
import os
import codecs
from pathlib import Path

import requests
import ssl

# Removed unverified SSL context for better security
# ssl._create_default_https_context = ssl._create_unverified_context

from geopy.geocoders import Nominatim
from instagram_private_api import Client as AppClient
from instagram_private_api import ClientCookieExpiredError, ClientLoginRequiredError, ClientError, ClientThrottledError

from prettytable import PrettyTable

# Ensure src modules exist before importing
try:
    from src import printcolors as pc
    from src import config
except ImportError:
    print("Warning: Missing src modules (printcolors, config). Some features may not work.")

class Osintgram:
    api = None
    api2 = None
    geolocator = Nominatim(user_agent="osintgram-bot")  # Updated User-Agent
    user_id = None
    target_id = None
    is_private = True
    following = False
    target = ""
    writeFile = False
    jsonDump = False
    cli_mode = False
    output_dir = "output"

    def __init__(self, target, is_file, is_json, is_cli, output_dir, clear_cookies):
        self.output_dir = output_dir or self.output_dir        
        u = getattr(config, 'getUsername', lambda: None)()
        p = getattr(config, 'getPassword', lambda: None)()

        if not u or not p:
            print("Error: Missing credentials in config.")
            sys.exit(1)

        self.clear_cookies(clear_cookies)
        self.cli_mode = is_cli
        if not is_cli:
            print("
Attempting to login...")

        self.login(u, p)
        self.setTarget(target)
        self.writeFile = is_file
        self.jsonDump = is_json

    def clear_cookies(self, clear_cookies):
        if clear_cookies:
            self.clear_cache()

    def setTarget(self, target):
        self.target = target
        user = self.get_user(target)
        if not user:
            print(f"Error: Could not retrieve user info for {target}.")
            return

        self.target_id = user.get('id')
        self.is_private = user.get('is_private')
        self.following = self.check_following()
        self.__printTargetBanner__()

        self.output_dir = os.path.join(self.output_dir, str(self.target))
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def get_user(self, username):
        try:
            content = self.api.username_info(username)
            return {'id': content['user']['pk'], 'is_private': content['user']['is_private']}
        except ClientError as e:
            print(f"ClientError: {e.msg}. Invalid username or network issue.")
            return None

    def check_following(self):
        if str(self.target_id) == self.api.authenticated_user_id:
            return True

        try:
            endpoint = f'users/{self.target_id}/full_detail_info/'
            response = self.api._call_api(endpoint)
            return response['user_detail']['user']['friendship_status']['following']
        except Exception:
            return False

    def login(self, u, p):
        try:
            settings_file = "config/settings.json"
            if not os.path.isfile(settings_file):
                print(f'Unable to find file: {settings_file}. Creating new login session.')
                self.api = AppClient(auto_patch=True, authenticate=True, username=u, password=p,
                                     on_login=lambda x: self.onlogin_callback(x, settings_file))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=self.from_json)

                self.api = AppClient(username=u, password=p, settings=cached_settings,
                                     on_login=lambda x: self.onlogin_callback(x, settings_file))
        except (ClientCookieExpiredError, ClientLoginRequiredError):
            print("Session expired. Logging in again.")
            self.api = AppClient(auto_patch=True, authenticate=True, username=u, password=p)
        except ClientError as e:
            print(f"Login failed: {e.msg}. Check credentials or Instagram restrictions.")
            sys.exit(1)

    def to_json(self, python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes', '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    def from_json(self, json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object

    def onlogin_callback(self, api, new_settings_file):
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=self.to_json)
            print(f"Session saved: {new_settings_file}")

    def clear_cache(self):
        try:
            with open("config/settings.json", 'w') as f:
                f.write("{}")
            print("Cache Cleared.")
        except FileNotFoundError:
            print("Error: Settings.json does not exist.")

# Additional methods go here...
