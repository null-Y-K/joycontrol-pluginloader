from enum import Enum, IntEnum
import os
import json
import logging
import argparse

import pygame
import asyncio
from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from JoycontrolPlugin.commands import JoycontrolCommands


logger = logging.getLogger(__name__)

# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)
# logger.propagate = False

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


class DualShock4StickDefinition(Enum):
    CENTER = {
        'axis1_range' : (-0.20, 0.20),
        'axis2_range' : (-0.20, 0.20)
    }

    UP = {
        'axis1_range' : (-1.00, -0.20),
        'axis2_range' : (-0.40, 0.40)
    }

    UP_LEFT = {
        'axis1_range' : (-1.00, -0.41),
        'axis2_range' : (-1.00, -0.20)
    }

    LEFT = {
        'axis1_range' : (-0.40, 0.40),
        'axis2_range' : (-1.00, -0.20)
    }

    DOWN_LEFT = {
        'axis1_range' : (0.41, 1.00),
        'axis2_range' : (-1.00, -0.20)
    }

    DOWN = {
        'axis1_range' : (0.20, 1.00),
        'axis2_range' : (-0.40, 0.40)
    }

    DOWN_RIGHT = {
        'axis1_range' : (0.41, 1.00),
        'axis2_range' : (0.20, 1.00)
    }

    RIGHT = {
        'axis1_range' : (-0.40, 0.40),
        'axis2_range' : (0.20, 1.00)
    }

    UP_RIGHT = {
        'axis1_range' : (-1.00, -0.41),
        'axis2_range' : (0.20, 1.00)
    }


class DualShock4CrossKeyDefinition(Enum):
    CENTER = (0, 0)
    UP = (0, 1)
    UP_LEFT = (-1, 1)
    LEFT = (-1, 0)
    DOWN_LEFT = (-1, -1)
    DOWN = (0, -1)
    DOWN_RIGHT = (1, -1)
    RIGHT = (1, 0)
    UP_RIGHT = (1, 1)



class SwitchStickDefinitionForDualshock4(Enum):
    CENTER = 'center'
    UP = 'up'
    UP_LEFT = 'up-left'
    LEFT = 'left'
    DOWN_LEFT = 'down-left'
    DOWN = 'down'
    DOWN_RIGHT = 'down-right'
    RIGHT = 'right'
    UP_RIGHT = 'up-right'


class SwitchButtonDefinitionForDualshock4(Enum):
    CROSS = 'b'
    CIRCLE = 'a'
    TRIANGLE = 'x'
    SQUARE = 'y'
    L1 = 'l'
    R1 = 'r'
    L2 = 'zl'
    R2 = 'zr'
    SHARE = 'minus'
    OPTIONS = 'plus'
    PS_HOME = 'home'
    L3 = 'l_stick'
    R3 = 'r_stick'


class SwitchCrossKeyDefinitionForDualshock4(Enum):
    CENTER = ('up', 'left', 'right', 'down')
    UP = ('up',)
    UP_LEFT = ('up', 'left')
    LEFT = ('left',)
    DOWN_LEFT = ('down', 'left')
    DOWN = ('down',)
    DOWN_RIGHT = ('down', 'right')
    RIGHT = ('right',)
    UP_RIGHT = ('up', 'right')

class JoycontrolDualShock4Error(Exception):
    pass


class JoycontrolDualShock4(JoycontrolCommands):
    def __init__(self, controller_state, recording=False):
        super().__init__(controller_state)
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        pygame.init()
        pygame.display.set_mode((320, 320))

        self.command_list = []
        self.recording_dict = {'recording_command': []}
        self.recording = recording

    def is_quit(self, event):
        return (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT

    def is_stick_value_in_range(self, stick_left_right_value, stick_up_down_value, stick_direction):
        axis1_lower_limit = stick_direction.value['axis1_range'][0]
        axis1_upper_limit = stick_direction.value['axis1_range'][1]
        result_1 = (axis1_lower_limit <= stick_up_down_value and stick_up_down_value <= axis1_upper_limit)

        axis2_lower_limit = stick_direction.value['axis2_range'][0]
        axis2_upper_limit = stick_direction.value['axis2_range'][1]
        result_2 = (axis2_lower_limit <= stick_left_right_value and stick_left_right_value <= axis2_upper_limit)

        return result_1 and result_2

    def get_stick_direction(self, stick_left_right_value, stick_up_down_value):
        _stick_left_right_value = round(stick_left_right_value, 2)
        _stick_up_down_value =  round(stick_up_down_value, 2)

        # center
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.CENTER)):
            return SwitchStickDefinitionForDualshock4.CENTER

        # up
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.UP)):
            return SwitchStickDefinitionForDualshock4.UP

        # up left
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.UP_LEFT)):
            return SwitchStickDefinitionForDualshock4.UP_LEFT

        # left
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.LEFT)):
            return SwitchStickDefinitionForDualshock4.LEFT

        # down left
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.DOWN_LEFT)):
            return SwitchStickDefinitionForDualshock4.DOWN_LEFT

        # down
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.DOWN)):
            return SwitchStickDefinitionForDualshock4.DOWN

        # down right
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.DOWN_RIGHT)):
            return SwitchStickDefinitionForDualshock4.DOWN_RIGHT

        # right
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.RIGHT)):
            return SwitchStickDefinitionForDualshock4.RIGHT

        # up right
        if (self.is_stick_value_in_range(
                _stick_left_right_value,
                _stick_up_down_value,
                DualShock4StickDefinition.UP_RIGHT)):
            return SwitchStickDefinitionForDualshock4.UP_RIGHT

    def get_l_stick_direction(self, event):
        if event.type == pygame.JOYAXISMOTION:
            l_stick_left_right = self.joystick.get_axis(int(DualShock4Axis.L_STICK_LEFT_RIGHAT))
            l_stick_up_down = self.joystick.get_axis(int(DualShock4Axis.L_STICK_UP_DOWN))
            logger.debug(f'L Stick Left Right: {l_stick_left_right}')
            logger.debug(f'L Stick Up Down   : {l_stick_up_down}')
            return self.get_stick_direction(l_stick_left_right, l_stick_up_down)

    def get_r_stick_direction(self, event):
        if event.type == pygame.JOYAXISMOTION:
            r_stick_left_right = self.joystick.get_axis(int(DualShock4Axis.R_STICK_LEFT_RIGHAT))
            r_stick_up_down = self.joystick.get_axis(int(DualShock4Axis.R_STICK_UP_DOWN))
            logger.debug(f'R Stick Left Right: {r_stick_left_right}')
            logger.debug(f'R Stick Up Down   : {r_stick_up_down}')
            return self.get_stick_direction(r_stick_left_right, r_stick_up_down)

    def get_cross_key_direction(self, event):
        if event.type == pygame.JOYHATMOTION:
            cross_key_value = self.joystick.get_hat(int(DualShock4HatSwitch.CROSS_KEY))
            logger.debug(f'Cross Key Value: {cross_key_value}')

            for cross_key_direction in DualShock4CrossKeyDefinition:
                if cross_key_direction.value == cross_key_value:
                    return SwitchCrossKeyDefinitionForDualshock4[cross_key_direction.name]
            return SwitchCrossKeyDefinitionForDualshock4.CENTER

    def get_button_down(self, event):
        if event.type == pygame.JOYBUTTONDOWN:
            button_name = DualShock4Botton(event.button).name
            logger.debug(f'Button Down : {button_name}')
            return SwitchButtonDefinitionForDualshock4[button_name]

    def get_button_up(self, event):
        if event.type == pygame.JOYBUTTONUP:
            button_name = DualShock4Botton(event.button).name
            logger.debug(f'Button Up : {DualShock4Botton(event.button).name}')
            return SwitchButtonDefinitionForDualshock4[button_name]

    def save_recording_command_to_json_file(self):
        if not self.recording:
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        no = 1
        json_file = ''
        while True:
            json_file = f'{script_dir}/recorded_command_{no}.json'
            if not os.path.exists(json_file):
                break
            no += 1
        with open(json_file, 'w') as f:
            json.dump(self.recording_dict, f, indent=2, ensure_ascii=False)

    def recording_commnad(self, command, type, direction, state):
        if not self.recording:
            return

        self.recording_dict['recording_command'].append(
            {
                "command": command,
                "type": type,
                "direction": direction,
                "state": state
            })


    async def main_loop(self):
        pygame.display.set_mode((320, 320))
        previous_l_stick_direction = None
        previous_r_stick_direction = None
        while True:
            for event in pygame.event.get():
                if self.is_quit(event):
                    pygame.quit()
                    return
                l_stick_direction = self.get_l_stick_direction(event)
                if l_stick_direction and (previous_l_stick_direction != l_stick_direction):
                    # print(f'L Stick Direction : {l_stick_direction.name}')
                    await self.left_stick(l_stick_direction.value)
                    previous_l_stick_direction = l_stick_direction
                    self.recording_commnad('stick', 'l_stick', l_stick_direction.value, '')

                r_stick_direction = self.get_r_stick_direction(event)
                if r_stick_direction and (previous_r_stick_direction != r_stick_direction):
                    # print(f'R Stick Direction : {r_stick_direction.name}')
                    await self.right_stick(r_stick_direction.value)
                    previous_r_stick_direction = r_stick_direction
                    self.recording_commnad('stick', 'r_stick', l_stick_direction.value, '')

                button_release = self.get_button_up(event)
                if button_release:
                    # print(f'Button Release : {button_release.name}')
                    await self.button_release(button_release.value)
                    self.recording_commnad('button', button_release.value, 'release', '')

                button_press = self.get_button_down(event)
                if button_press:
                    # print(f'Button Press : {button_press.name}')
                    await self.button_press(button_press.value)
                    self.recording_commnad('button', button_press.value, 'press', '')

                cross_key_direction = self.get_cross_key_direction(event)
                if cross_key_direction:
                    if cross_key_direction == SwitchCrossKeyDefinitionForDualshock4.CENTER:
                        # print(f'Cross Key Release : {cross_key_direction.name}')
                        await self.button_release(*cross_key_direction.value)
                        self.recording_commnad('button', ', '.join(cross_key_direction.value), 'release', '')
                    else:
                        # print(f'Cross Key Press : {cross_key_direction.name}')
                        await self.button_press(*cross_key_direction.value)
                        self.recording_commnad('button', ', '.join(cross_key_direction.value), 'press', '')
            await self.wait(0.1)
            self.recording_commnad('wait', '', '', '')


async def start(reconnect_bt_addr, recording):
    # Create memory containing default controller stick calibration
    spi_flash = FlashMemory()

    # Get controller name to emulate from arguments
    controller = Controller.from_arg('PRO_CONTROLLER')

    with utils.get_output(path=None, default=None) as capture_file:
        factory = controller_protocol_factory(controller, spi_flash=spi_flash)
        ctl_psm, itr_psm = 17, 19
        transport, protocol = await create_hid_server(factory, reconnect_bt_addr=reconnect_bt_addr,
                                                        ctl_psm=ctl_psm,
                                                        itr_psm=itr_psm, capture_file=capture_file,
                                                        device_id=None)

    controller_state = protocol.get_controller_state()
    transport = transport
    try:
        # waits until controller is fully connected
        await controller_state.connect()
        dualshock = JoycontrolDualShock4(controller_state, recording)
        await dualshock.main_loop()
        dualshock.save_recording_command_to_json_file()
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('Stopping communication...')
        await transport.close()
        transport = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address, for reconnecting as an already paired controller')
    parser.add_argument('--recording', action='store_true', help='Record commands operated on the gamepad')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start(args.reconnect_bt_addr, args.recording))
    except KeyboardInterrupt:
        pass