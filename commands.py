import os
import webbrowser
from typing import Dict, List, Any
from abc import abstractmethod
import xml.etree.ElementTree as ET

from resource_checker import Resource


class Command:
    def __init__(self, name: str, shortcut: str, description: str = ""):
        self._name: str
        self._shortcut: str
        self._description: str

        self.name = name
        self.shortcut = shortcut
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if value is None:
            raise ValueError("Name cannot be None!")
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def shortcut(self):
        return self._shortcut

    @shortcut.setter
    def shortcut(self, value: str):
        if value is None:
            raise ValueError("Shortcut cannot be None!")
        self._shortcut = value

    @classmethod
    @abstractmethod
    def from_xml_element(cls, node: ET.Element, settings: Dict[str, Any]):
        pass


class WebBrowserUrlCommand(Command):
    DUMMY_URL: str = "google.com"

    def __init__(self, name: str, shortcut: str, page_url: str, description: str = None,
                 browser: webbrowser.BaseBrowser = None):
        super().__init__(name, shortcut, description)
        self._page_url: str
        self._browser: webbrowser.BaseBrowser

        self.browser = browser
        self.page_url = page_url

    @property
    def page_url(self):
        return self._page_url

    @page_url.setter
    def page_url(self, value: str):
        self._page_url = value if value is not None else WebBrowserUrlCommand.DUMMY_URL

    @property
    def browser(self):
        return self._browser

    @browser.setter
    def browser(self, value: webbrowser.BaseBrowser):
        if value is None:
            raise ValueError("Browser can't be None!")
        self._browser = value

    def execute(self):
        self.browser.open(self._page_url)

    @classmethod
    def from_xml_element(cls, node: ET.Element, settings: Dict[str, Any] = None):
        if settings is None:
            settings = CommandManager.__default_settings__
        name = node.find("name").text
        shortcut = node.find("shortcut").text
        page_url = node.find("page-url").text

        description_node = node.find("description")
        description = description_node.text if description_node is not None else None

        # In case we have found a particular <browser> tag for a command - we state it. Otherwise, we use default
        # browser path which we have specified in <settings> tag in the root.
        browser_node = node.find("browser")
        browser = webbrowser.get(browser_node.get("path")) if browser_node else settings['default-browser']
        return cls(name, shortcut, page_url, description, browser)


class BashCommand(Command):
    def __init__(self, name: str, shortcut: str, text: str, description: str = None):
        super().__init__(name, shortcut, description)
        self._text: str

        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        if value is None:
            raise ValueError("Text cannot be None!")
        self._text = value

    def execute(self):
        os.system(self._text)

    @classmethod
    def from_xml_element(cls, node: ET.Element, settings: Dict[str, Any] = None):
        if settings is None:
            settings = CommandManager.__default_settings__
        name = node.find("name").text
        shortcut = node.find("shortcut").text
        text = node.find("text").text

        description_node = node.find("description")
        description = description_node.text if description_node is not None else None

        return cls(name, shortcut, text, description)


class CommandManager(Resource):
    __default_settings__: Dict[str, Any] = {
        "default-browser": None,
        "include-path-commands": False
    }

    def __init__(self, commands: List[Command], settings: Dict[str, Any] = None, source_path: str | None = None):
        super().__init__(source_path)
        self._commands: Dict[str, Command] = {command.shortcut: command for command in commands}
        if settings is None:
            settings = CommandManager.__default_settings__.copy()
        self._settings = settings

    @staticmethod
    def from_xml(xml_path: str) -> 'CommandManager':
        root: ET.Element
        if xml_path is not None:
            root = ET.parse(xml_path).getroot()
        else:
            raise ValueError("xml_path was None!")

        # +------- Parsing settings -------+
        settings = CommandManager.__default_settings__.copy()
        settings_xml_element = root.find('settings')  # noqa

        if settings_xml_element:
            default_browser_xml_value = settings_xml_element.find("browser")
            if default_browser_xml_value is not None:
                settings['default-browser'] = webbrowser.get(default_browser_xml_value.get("path"))

        # +------- Parsing commands -------+

        command_block = root.find('commands')
        command_list = []
        for command_xml_element in command_block:
            match command_xml_element.tag:
                case "web-command":
                    command = WebBrowserUrlCommand.from_xml_element(command_xml_element, settings)
                case "bash-command":
                    command = BashCommand.from_xml_element(command_xml_element, settings)
                case _:
                    raise ValueError(f"Wrong command tag: {command_xml_element.tag}!")
            command_list.append(command)

        # +------- Returning result -------+
        return CommandManager(command_list, settings=settings, source_path=xml_path)

    @property
    def settings(self):
        return self._settings

    @property
    def commands(self):
        return self._commands
