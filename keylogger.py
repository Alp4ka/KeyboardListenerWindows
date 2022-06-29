from abc import abstractmethod
from enum import IntEnum
from typing import List

import keyboard
from time import time as now
from commands import CommandManager
from timer import RestartableTimer


class KeyLoggerCallback:
    @abstractmethod
    def clear_input(self):
        pass

    @abstractmethod
    def set_input(self, value: str):
        pass

    @abstractmethod
    def get_input(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

    @abstractmethod
    def toggle_state(self):
        pass

    @abstractmethod
    def close(self):
        pass


class ProgramState(IntEnum):
    ACTIVE = 0
    PAUSE = 1

    def __invert__(self):
        return ProgramState(ProgramState.PAUSE.value - self.value)

    def is_active(self):
        return self == ProgramState.ACTIVE


class KeyLogger:
    EXIT_KEY = "esc"
    STATE_HOT_KEY = "ctrl + k + l"
    ENTER_KEY = "!"
    TIME_READING_CONSTRAINTS = 0.6
    ALPHABET = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"

    def __init__(self, command_manager: CommandManager, callback: KeyLoggerCallback = None):
        self.__callback: KeyLoggerCallback = callback
        self.__command_manager: CommandManager = command_manager
        self.__state: ProgramState = ProgramState.PAUSE
        self.__event_buffer: List = []
        self.__txt_buffer: str = ""
        self.__is_reading: bool = False
        self.__read_start_time: int = -1
        self.__input_time_constraints_checker: RestartableTimer = RestartableTimer(self.TIME_READING_CONSTRAINTS,
                                                                                   self.__validate_time_constraints)

    def __invert_state(self):
        self.__set_state(~self.__state)

    def __set_state(self, state):
        self.__state = state
        if state == ProgramState.PAUSE:
            self.__callback.hide()

    def __key_press_event_handler(self, event: keyboard.KeyboardEvent):
        if not self.__state.is_active():
            return

        if event.name == KeyLogger.ENTER_KEY:
            self.__start_reading(event.time)
            return

        if not self.__is_reading:
            return

        if event.name in KeyLogger.ALPHABET:
            self.__input_time_constraints_checker.restart()
            self.__add_to_buffs(event)

    def __try_execute(self, shortcut_text: str) -> bool:
        if shortcut_text in self.__command_manager.commands.keys():
            self.__command_manager.commands[shortcut_text].execute()
            self.__stop_reading()
            return True
        return False

    def __clear(self):
        self.__txt_buffer = ""
        self.__event_buffer.clear()
        self.__callback.clear_input()

    def __start_reading(self, start_time):
        self.__input_time_constraints_checker.start()
        self.__clear()
        self.__is_reading = True
        self.__read_start_time = start_time
        self.__callback.show()

    def __stop_reading(self):
        self.__input_time_constraints_checker.cancel()
        self.__clear()
        self.__is_reading = False
        self.__read_start_time = -1
        self.__callback.hide()

    def __is_in_time_constraints(self, time) -> bool:
        if not self.__event_buffer:
            if self.__read_start_time == -1:
                return False
            previous_time = self.__read_start_time
        else:
            previous_time = self.__event_buffer[-1].time
        delta = time - previous_time
        return delta <= KeyLogger.TIME_READING_CONSTRAINTS

    def __validate_time_constraints(self):
        if not self.__is_in_time_constraints(now()):
            if not self.__try_execute(self.__txt_buffer):
                self.__stop_reading()

    def __add_to_buffs(self, event: keyboard.KeyboardEvent):
        self.__event_buffer.append(event)
        self.__txt_buffer += event.name
        self.__callback.set_input(self.__txt_buffer)

    def start(self):
        self.__callback.hide() if self.__callback else None
        self.__callback.clear_input() if self.__callback else None
        self.__set_state(ProgramState.ACTIVE)
        keyboard.add_hotkey(self.STATE_HOT_KEY, self.__invert_state)
        keyboard.on_release(callback=self.__key_press_event_handler)
        keyboard.wait(KeyLogger.EXIT_KEY)
        self.finish()

    def finish(self):
        self.__set_state(ProgramState.PAUSE)
        self.__clear()
