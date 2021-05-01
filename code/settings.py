
import configparser
import os


FILENAME = "settings.ini"
FILEPATH = "config"
HOTKEYS_SECTION = "HOTKEYS"

ERROR_OK = 0
ERROR_GET = 1
ERROR_PUT = 2
ERROR_PATH = 3
ERROR_SAVE = 4
ERROR_LOAD = 5


class Settings(object):

    def __init__(self, file_name, path):
        self.config = configparser.ConfigParser()
        self.file_name = file_name
        self.path = path
        self.loaded = False
        self.saved = True
        self.error = ERROR_OK  # get: 1, put: 2, save: 3,4, load: 5,6

    def get(self, section, key=None):
        val = None

        if (key == None):
            val = self.config[section]

        try:
            val = self.config[section][key]
        except Exception as e:
            print("Settings.get: Could not get", e)
            self.error = ERROR_GET

        return val

    def put(self, section, key, value):
        if (not self.config.has_section(section)):
            self.config[section] = {}
        self.config[section][key] = value
        self.saved = False

    def save(self):
        if (self.error != ERROR_OK):
            print("Forbid to save. Error:", self.error)

        path_back = os.getcwd()
        try:
            os.chdir(self.path)
        except Exception as e:
            print("Settings.save -> chdir:", self.path, e)
            self.error = ERROR_PATH
        if (self.error == ERROR_OK):
            try:
                f = open(self.file_name, 'w')
                self.config.write(f)
                f.close()
                self.error = ERROR_OK
                self.saved = True
            except Exception as e:
                print("Settings.save -> config.write:", self.file_name, e)
                self.error = ERROR_SAVE
        os.chdir(path_back)

    def load(self):
        path_back = os.getcwd()
        try:
            os.chdir(self.path)
            self.error = ERROR_OK
        except Exception as e:
            print("Settings.load -> chdir:", self.path, e)
            self.error = ERROR_PATH

        if (self.error != ERROR_PATH): # If path is ok -> load
            try:
                f = open(self.file_name, 'r')  # check that file exist
                f.close()
                self.config.read(self.file_name)
                self.error = ERROR_OK
                self.loaded = True
            except Exception as e:
                print("Settings.load -> config.read:", self.file_name, e)
                self.error = ERROR_LOAD
        os.chdir(path_back)

    def isSaved(self):
        return self.saved

    def isLoaded(self):
        return self.loaded

    def getErrorStatus(self):
        return self.error


def get(section, key):
    return settings.get(section, key)


def get_hotkeys():
    return settings.get(HOTKEYS_SECTION)


def getErrorStatus():
    return settings.getErrorStatus()


# FILENAME and FILEPATH are constants
# If path FILEPATH is not exist then ERROR_PATH
# If file FILENAME is not exist in folder FILEPATH then ERROR_LOAD
settings = Settings(FILENAME, FILEPATH)
settings.load()
