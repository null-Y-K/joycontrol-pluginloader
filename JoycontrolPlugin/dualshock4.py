
from abc import abstractmethod
from enum import Enum, IntEnum
import logging

import pygame
from JoycontrolPlugin.commands import JoycontrolCommands

logger = logging.getLogger(__name__)

class DualShock4Botton(IntEnum):
    CROSS = 0
    CIRCLE = 1
    TRIANGLE = 2
    SQUARE = 3
    L1 = 4
    R1 = 5
    L2 = 6
    R2 = 7
    SHARE = 8
    OPTIONS = 9
    PS_HOME = 10
    L3 = 11
    R3 = 12
    TOUCH_PAD = 13
    NO_DEFINITION = 14


class DualShock4Axis(IntEnum):
    L_STICK_LEFT_RIGHAT = 0
    L_STICK_UP_DOWN = 1
    L2_TRIGGER = 2
    R_STICK_LEFT_RIGHAT = 3
    R_STICK_UP_DOWN = 4
    R2_TRIGGER = 5


class DualShock4HatSwitch(IntEnum):
    CROSS_KEY = 0


class AxisDefinition(Enum):
    CENTER_UPPER_LIMIT = 0.10
    CENTER_LOWER_LIMIT = -0.10

    UP_STRONG_UPPER_LIMIT = 1.00
    UP_STRONG_LOWER_LIMIT = 0.51

    UP_WEAK_UPPER_LIMIT = 0.50
    UP_WEAK_LOWER_LIMIT = 0.11

    DOWN_STRONG_UPPER_LIMIT = -1.00
    DOWN_STRONG_LOWER_LIMIT = -0.51

    DOWN_WEAK_UPPER_LIMIT = -0.50
    DOWN_WEAK_LOWER_LIMIT = -0.11

    LEFT_STRONG_UPPER_LIMIT = 1.00
    LEFT_STRONG_LOWER_LIMIT = 0.51

    LEFT_WEAK_UPPER_LIMIT = 0.50
    LEFT_WEAK_LOWER_LIMIT = 0.11

    RIGHT_STRONG_UPPER_LIMIT = -1.00
    RIGHT_STRONG_LOWER_LIMIT = -0.51

    RIGHT_WEAK_UPPER_LIMIT = -0.50
    RIGHT_WEAK_LOWER_LIMIT = -0.11


class StickDirection(IntEnum):
    CENTER = 0
    UP = 1
    UP_LEFT = 2
    LEFT = 3
    DOWN_LEFT = 4
    DOWN = 5
    DOWN_RIGHT = 6
    RIGHT = 7
    UP_RIGHT = 8


class StickPower(IntEnum):
    NONE = 0
    STRONG = 1
    WEAK = 2


class JoycontrolDualShock4Error(Exception):
    pass


class JoycontrolDualShock4(JoycontrolCommands):
    def __init__(self, controller_state):
        super().__init__(controller_state)
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        pygame.init()
        pygame.display.set_mode((320, 320))

        self.CENTER_UPPER_LIMIT

    def is_quit(self, event):
        return (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT

    def is_value_in_range(self, value, lower_limit, upper_limit):
        return (lower_limit < value and value < upper_limit)

    def calc_stick_direction(self, stick_left_right_value, stick_up_down_value):
        # center
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.CENTER_LOWER_LIMIT, AxisDefinition.CENTER_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.CENTER_LOWER_LIMIT, AxisDefinition.CENTER_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.CENTER, StickPower.NONE)

        # up strong
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.RIGHT_WEAK_UPPER_LIMIT, AxisDefinition.LEFT_WEAK_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.UP_STRONG_LOWER_LIMIT, AxisDefinition.UP_STRONG_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.UP, StickPower.STRONG)

        # up weak
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.RIGHT_WEAK_LOWER_LIMIT, AxisDefinition.LEFT_WEAK_LOWER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.UP_WEAK_LOWER_LIMIT, AxisDefinition.UP_WEAK_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.UP, StickPower.WEAK)

        # up left strong
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_STRONG_LOWER_LIMIT, AxisDefinition.LEFT_STRONG_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.UP_STRONG_LOWER_LIMIT, AxisDefinition.UP_STRONG_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.UP_LEFT, StickPower.STRONG)

        # up left weak
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_WEAK_LOWER_LIMIT, AxisDefinition.LEFT_WEAK_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.UP_WEAK_LOWER_LIMIT, AxisDefinition.UP_WEAK_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.UP_LEFT, StickPower.WEAK)

        # left strong
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_STRONG_LOWER_LIMIT, AxisDefinition.LEFT_STRONG_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.DOWN_WEAK_UPPER_LIMIT, AxisDefinition.UP_WEAK_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.LEFT, StickPower.STRONG)

        # left weak
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_WEAK_LOWER_LIMIT, AxisDefinition.LEFT_WEAK_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.DOWN_WEAK_LOWER_LIMIT, AxisDefinition.UP_WEAK_LOWER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.LEFT, StickPower.WEAK)

        # down left strong
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_STRONG_LOWER_LIMIT, AxisDefinition.LEFT_STRONG_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.DOWN_STRONG_LOWER_LIMIT, AxisDefinition.DOWN_STRONG_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.DOWN_LEFT, StickPower.STRONG)

        # down left weak
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.LEFT_WEAK_LOWER_LIMIT, AxisDefinition.LEFT_WEAK_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.DOWN_WEAK_LOWER_LIMIT, AxisDefinition.DOWN_WEAK_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.DOWN_LEFT, StickPower.STRONG)

        # down strong
        result_1 = self.is_value_in_range(stick_left_right_value, AxisDefinition.RIGHT_WEAK_UPPER_LIMIT, AxisDefinition.LEFT_WEAK_UPPER_LIMIT)
        result_2 = self.is_value_in_range(stick_up_down_value, AxisDefinition.DOWN_STRONG_LOWER_LIMIT, AxisDefinition.DOWN_STRONG_UPPER_LIMIT)
        if result_1 and result_2:
            return (StickDirection.UP, StickPower.STRONG)



    def get_l_stick_axis(self, event):
        if event.type == pygame.JOYAXISMOTION:
            l_stick_left_right = self.joystick.get_axis(int(DualShock4Axis.L_STICK_LEFT_RIGHAT))
            l_stick_up_down = self.joystick.get_axis(int(DualShock4Axis.L_STICK_UP_DOWN))
            logger.debug(f'L Stick Left Right: {l_stick_left_right}')
            logger.debug(f'L Stick Up Down   : {l_stick_up_down}')

    def get_r_stick_axis(self, event):
        if event.type == pygame.JOYAXISMOTION:
            r_stick_left_right = self.joystick.get_axis(int(DualShock4Axis.R_STICK_LEFT_RIGHAT))
            r_stick_up_down = self.joystick.get_axis(int(DualShock4Axis.R_STICK_UP_DOWN))
            logger.debug(f'R Stick Left Right: {r_stick_left_right}')
            logger.debug(f'R Stick Up Down   : {r_stick_up_down}')

    def get_cross_key_axis(self, event):
        if event.type == pygame.JOYHATMOTION:
            cross_key_value = self.joystick.get_hat(int(DualShock4HatSwitch.CROSS_KEY))
            logger.debug(f'Cross Key Value: {cross_key_value}')

    def get_button_down(self, event):
        if event.type == pygame.JOYBUTTONDOWN:
            logger.debug(f'Button Down : {DualShock4Botton(event.button).name}')

    def get_button_up(self, event):
        if event.type == pygame.JOYBUTTONUP:
            logger.debug(f'Button Up : {DualShock4Botton(event.button).name}')

    @abstractmethod
    async def run(self):
        pass


if __name__ == '__main__':
    print("test")