import sys
from os.path import abspath, dirname

sys.path.append(dirname(abspath(__file__)))

from commands import CommandManager # noqa
from keylogger import KeyLogger # noqa
from gui import MainApp # noqa


def main(*args, **kwargs):
    gui = MainApp()
    gui.daemon = True
    gui.start()

    command_manager = CommandManager.from_xml("./resources/commands.xml")
    key_logger = KeyLogger(command_manager, callback=gui)
    try:
        key_logger.start()
    except KeyboardInterrupt:
        key_logger.finish()
    finally:
        exit(0)


if __name__ == "__main__":
    main(sys.argv)
