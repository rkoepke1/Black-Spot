#!/usr/bin/python
# -*- coding: utf-8 -*-

from asyncore import file_dispatcher, loop
from threading import Thread
import black_spot

try:
    from evdev import InputDevice, list_devices, ecodes
except ImportError:
    print ('Not importing evdev, expected during sphinx generation on OSX')
'''
        if (self.joysticks[0].get_axis(1) > 0.1 or self.joysticks[0].get_axis(1) < -0.1 or self.joysticks[0].get_axis(0) > 0.1 or self.joysticks[0].get_axis(0) < -0.1):
            if self.joysticks[0].get_button(self.buttons['x']) == 1:
                print("x")
                lock *= -1
                servo_pos1 = jAxis - (self.joysticks[0].get_axis(0) * const.SERVO_CENTER)
                servo_pos2 = jAxis - (self.joysticks[0].get_axis(1) * const.SERVO_CENTER)
            else:
                self.rotate_servo(const.SERVO2, jAxis - (self.joysticks[0].get_axis(0) * const.SERVO_CENTER))
                self.rotate_servo(const.SERVO3, jAxis - (self.joysticks[0].get_axis(1) * const.SERVO_CENTER))
        else:
        
            if lock > 0:
                self.rotate_servo(const.SERVO2, servo_pos1)
                self.rotate_servo(const.SERVO3, servo_pos2)
            else:
                self.rotate_servo(const.SERVO2, jAxis)
                self.rotate_servo(const.SERVO3, jAxis)
             
                 
        if self.joysticks[0].get_button(self.buttons['r1']) == 1:
            print(self.buttons['r1'])
            self.board.digital[const.RIGHT_DIGI1].write(const.HIGH)
            self.board.digital[const.RIGHT_DIGI2].write(const.LOW)
            self.board.digital[const.RIGHT_PWM].write(const.HIGH)
        elif self.joysticks[0].get_button(self.buttons['r2']) == 1:
            print(self.buttons['r2'])
            self.board.digital[const.RIGHT_DIGI1].write(const.LOW)
            self.board.digital[const.RIGHT_DIGI2].write(const.HIGH)
            self.board.digital[const.RIGHT_PWM].write(const.HIGH)
        else:
            self.board.digital[const.RIGHT_PWM].write(const.LOW)
            self.board.digital[const.LEFT_PWM].write(const.LOW)
            if (controller.get_axes()[1].value > 0.1 or controller.get_axes()[1].value < -0.1 or controller.get_axes()[0].value > 0.1 or controller.get_axes()[0].value < -0.1):
                r.rotate_servo(const.SERVO2, 90 - (controller.get_axes()[0].value * const.SERVO_CENTER))
            r.rotate_servo(const.SERVO3, 90 - (controller.get_axes()[1].value * const.SERVO_CENTER))
     '''       

class SixAxisResource:

    """
    Resource class which will automatically connect and disconnect to and from a joystick, creating a new SixAxis
    object and passing it to the 'with' clause. Also binds a handler to the START button which resets the axis
    calibration, and to the SELECT button which centers the analogue sticks on the current position.
    """

    def __init__(
        self,
        bind_defaults=False,
        dead_zone=0.05,
        hot_zone=0.0,
        ):
        """
        Resource class, produces a :class:`triangula.input.SixAxis` for use in a 'with' binding.

        :param float dead_zone:
            See SixAxis class documentation
        :param float hot_zone:
            See SixAxis class documentation
        :param bind_defaults:
            Defaults to False, if True will automatically bind two actions to the START and SELECT buttons to
            reset the axis calibration and to set the axis centers respectively.
        """

        self.bind_defaults = bind_defaults
        self.dead_zone = dead_zone
        self.hot_zone = hot_zone

    def __enter__(self):
        self.joystick = SixAxis(dead_zone=self.dead_zone,
                                hot_zone=self.hot_zone)
        self.joystick.connect()
        if self.bind_defaults:
            self.joystick.register_button_handler(self.joystick.reset_axis_calibration,
                    SixAxis.BUTTON_START)
            self.joystick.register_button_handler(self.joystick.set_axis_centers,
                    SixAxis.BUTTON_SELECT)
        return self.joystick

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
        ):
        self.joystick.disconnect()


class SixAxis:

    """
    Class to handle the PS3 SixAxis controller

    This class will process events from the evdev event queue and calculate positions for each of the analogue axes on
    the SixAxis controller (motion sensing is not currently supported). It will also extract
    button press events and call any handler functions bound to those buttons.

    Once the connect() call is made, a thread is created which will actively monitor the device for events, passing them
    to the SixAxis class for processing. There is no need to poll the event queue manually.

    Consuming code can get the current position of any of the sticks from this class through the `axes` instance
    property. This contains a list of :class:`triangula.input.SixAxis.Axis` objects, one for each distinct axis on the
    controller. The list of axes is, in order: left x, left y, right x, right y.
    """

    BUTTON_SELECT = 0  # : The Select button
    BUTTON_LEFT_STICK = 1  # : Left stick click button
    BUTTON_RIGHT_STICK = 2  # : Right stick click button
    BUTTON_START = 3  # : Start button
    BUTTON_D_UP = 4  # : D-pad up
    BUTTON_D_RIGHT = 5  # : D-pad right
    BUTTON_D_DOWN = 6  # : D-pad down
    BUTTON_D_LEFT = 7  # : D-pad left
    BUTTON_L2 = 8  # : L2 lower shoulder trigger
    BUTTON_R2 = 9  # : R2 lower shoulder trigger
    BUTTON_L1 = 10  # : L1 upper shoulder trigger
    BUTTON_R1 = 11  # : R1 upper shoulder trigger
    BUTTON_TRIANGLE = 12  # : Triangle
    BUTTON_CIRCLE = 13  # : Circle
    BUTTON_CROSS = 14  # : Cross
    BUTTON_SQUARE = 15  # : Square
    BUTTON_PS = 16  # : PS button

    def __init__(
        self,
        dead_zone=0.05,
        hot_zone=0.0,
        connect=False,
        ):
        """
        Discover and initialise a PS3 SixAxis controller connected to this computer.

        :param float dead_zone:
            Creates a dead zone centerd on the center position of the axis (which may or may not be zero depending on
            calibration). The axis values range from 0 to 1.0, but will be locked to 0.0 when the measured value less
            center offset is lower in magnitude than this supplied value. Defaults to 0.05, which makes the PS3 analogue
            sticks easy to center but still responsive to motion. The deadzone is applies to each axis independently, so
            e.g. moving the stick far right won't affect the deadzone for that sticks Y axis.
        :param float hot_zone:
            Creates a zone of maximum value, any readings from the sensor which are within this value of the max or min
            values will be mapped to 1.0 and -1.0 respectively. This can be useful because, while the PS3 controllers
            sticks have independent axes, they are constrained to move within a circle, so it's impossible to have e.g.
            1.0,1.0 for both x and y axes. Setting this value to non-zero in effect partially squares the circle,
            allowing for controls which require full range control. Setting this value to 1/sqrt(2) will create a square
            zone of variability within the circular range of motion of the controller, with any stick motions outside
            this square mapping to the maximum value for the respective axis. The value is actually scaled by the max
            and min magnitude for upper and lower ranges respectively, so e.g. setting 0.5 will create a hot-zone at
            above half the maximum value and below half the minimum value, and not at +0.5 and -0.5 (unless max and
            min are 1.0 and -1.0 respectively). As with the dead zone, these are applied separately to each axis, so in
            the case where the hot zone is set to 1/sqrt(2), a circular motion of the stick will map to x and y values
            which trace the outline of a square of unit size, allowing for all values to be emitted from the stick.
        :param connect:
            If true, call connect(), otherwise you need to call it elsewhere. Note that connect() may raise IOError if
            it can't find a PS3 controller, so it's best to call it explicitly yourself and handle the error. Defaults
            to False.
        :return: an initialised link to an attached PS3 SixAxis controller.
        """
        self.buttons_pressed = 0
        self.button_handlers = []
        self._stop_function = None
        self.axes = [SixAxis.Axis('left_x', dead_zone=dead_zone,
                     hot_zone=hot_zone), SixAxis.Axis('left_y',
                     dead_zone=dead_zone, hot_zone=hot_zone,
                     invert=True), SixAxis.Axis('right_x',
                     dead_zone=dead_zone, hot_zone=hot_zone),
                     SixAxis.Axis('right_y', dead_zone=dead_zone,
                     hot_zone=hot_zone, invert=True)]


        if connect:
            self.connect()

    def is_connected(self):
        """
        Check whether we have a connection

        :return:
            True if we're connected to a controller, False otherwise.
        """

        if self._stop_function:
            return True
        else:
            return False

    def get_and_clear_button_press_history(self):
        """
        Return the button press bitfield, clearing it as we do.

        :return:
            A bit-field where bits are set to 1 if the corresponding button has been pressed since the last call to
            this method. Test with e.g. 'if button_press_field & SixAxis.BUTTON_CIRCLE:...'
        """

        old_buttons = self.buttons_pressed
        self.buttons_pressed = 0
        return old_buttons

    def connect(self):
        """
        Connect to the first PS3 controller available within /dev/inputX, identifying it by name (this may mean
        that the code doesn't work with non-genuine PS3 controllers, I only have original ones so haven't had
        a chance to test).

        This also creates a new thread to run the asyncore loop, and uses a file dispatcher monitoring the corresponding
        device to handle input events. All events are passed to the handle_event function in the parent, this is then
        responsible for interpreting the events and updating any internal state, calling button handlers etc.

        :return:
            True if a controller was found and connected, False if we already had a connection
        :raises IOError:
            If we didn't already have a controller but couldn't find a new one, this normally means
            there's no controller paired with the Pi
        """

        if self._stop_function:
            return False
        for device in [InputDevice(fn) for fn in list_devices()]:
            print(device)
            if 'PLAYSTATION(R)3 Controller' in device.name:
                parent = self

                class InputDeviceDispatcher(file_dispatcher):

                    def __init__(self):
                        self.device = device
                        self.robot = black_spot.BlackSpot()
                        file_dispatcher.__init__(self, device)

                    def recv(self, ign=None):
                        return self.device.read()

                    def handle_read(self):
                        for event in self.recv():
                            print("code = {}, value = {}".format(event.code, event.value))
                            parent.handle_event(event, self.robot)

                    def handle_error(self):
                        pass

                class AsyncLoop(Thread):

                    def __init__(self, channel):
                        Thread.__init__(self, name='InputDispatchThread')
                        self.channel = channel

                    def run(self):
                        loop()

                    def stop(self):
                        self.channel.close()
                        
                
                loop_thread = AsyncLoop(InputDeviceDispatcher())
                self._stop_function = loop_thread.stop
                loop_thread.start()
                return True
                
        raise IOError('Unable to find a SixAxis controller')

    def disconnect(self):
        """
        Disconnect from any controllers, shutting down the channel and allowing the monitoring thread to terminate
        if there's nothing else bound into the evdev loop. Doesn't do anything if we're not connected to a controller
        """

        if self._stop_function:
            self._stop_function()
            self._stop_function = None

    def __str__(self):
        """
        Simple string representation of the state of the axes
        """

        return 'x1={}, y1={}, x2={}, y2={}'.format(self.axes[0].corrected_value(),
                self.axes[1].corrected_value(),
                self.axes[2].corrected_value(),
                self.axes[3].corrected_value())
    
    def get_axes(self):
        return self.axes 

    def set_axis_centers(self, *args):
        """
        Sets the center points for each axis to the current value for that axis. This center value is used when
        computing the value for the axis and is subtracted before applying any scaling.
        """

        for axis in self.axes:
            axis.center = axis.value

    def reset_axis_calibration(self, *args):
        """
        Resets any previously defined axis calibration to 0.0 for all axes
        """

        for axis in self.axes:
            axis._reset()

    def register_button_handler(self, button_handler, buttons):
        """
        Register a handler function which will be called when a button is pressed

        :param handler: a function which will be called when any of the specified buttons are pressed. The function is
            called with the integer code for the button as the sole argument.
        :param [int] buttons: a list or one or more buttons which should trigger the handler when pressed. Buttons are
            specified as ints, for convenience the PS3 button assignments are mapped to names in SixAxis, i.e.
            SixAxis.BUTTON_CIRCLE. This includes the buttons in each of the analogue sticks. A bare int value is also
            accepted here and will be treated as if a single element list was supplied.
        :return: a no-arg function which can be used to remove this registration
        """
        mask = 0
        if isinstance(buttons, list):
            for button in buttons:
                mask += 1 << button
        else:
            mask += 1 << buttons
        h = {'handler': button_handler, 'mask': mask}
        self.button_handlers.append(h)

        def remove():
            self.button_handlers.remove(h)

        return remove

    def handle_event(self, event, robot):
        """
        Handle a single evdev event, this updates the internal state of the Axis objects as well as calling any
        registered button handlers.

        :internal:

        :param event:
            The evdev event object to parse
        """
        if event.type == ecodes.EV_ABS:
            value = float(event.value) / 127
                       
            if event.code == 0:

                # Left stick, X axis
                robot.rotate_servo(180)
                
                robot.rotate_servo(0)
                
           
                    
                self.axes[0]._set(value)
            elif event.code == 1:

                # Left stick, Y axis

                self.axes[1]._set(value)
            elif event.code == 2:

                # Right stick, X axis

                self.axes[2]._set(value)
            elif event.code == 3:

                # Right stick, Y axis (yes, 5...)

                self.axes[3]._set(value)
                
        elif event.type == ecodes.EV_KEY:
        
            if event.value == 1:
                if event.code == 288:
                    button = SixAxis.BUTTON_SELECT
                elif event.code == 291:
                    button = SixAxis.BUTTON_START
                elif event.code == 289:
                    button = SixAxis.BUTTON_LEFT_STICK
                elif event.code == 290:
                    button = SixAxis.BUTTON_RIGHT_STICK
                elif event.code == 295:
                    button = SixAxis.BUTTON_D_LEFT
                elif event.code == 292:
                    button = SixAxis.BUTTON_D_UP
                elif event.code == 293:
                    button = SixAxis.BUTTON_D_RIGHT
                elif event.code == 294:
                    button = SixAxis.BUTTON_D_DOWN
                elif event.code == 704:
                    button = SixAxis.BUTTON_PS
                elif event.code == 303:
                    button = SixAxis.BUTTON_SQUARE
                elif event.code == 300:
                    button = SixAxis.BUTTON_TRIANGLE
                elif event.code == 301:
                    button = SixAxis.BUTTON_CIRCLE
                elif event.code == 302:
                    button = SixAxis.BUTTON_CROSS
                elif event.code == 299:
                    button = SixAxis.BUTTON_R1
                elif event.code == 297:
                    button = SixAxis.BUTTON_R2
                elif event.code == 298:
                    button = SixAxis.BUTTON_L1
                elif event.code == 296:
                    button = SixAxis.BUTTON_L2
                else:
                    button = None
                if button is not None:
                    print(1 << button)
                    self.buttons_pressed |= 1 << button
                    for button_handler in self.button_handlers:
                        if button_handler['mask'] & 1 << button != 0:
                            button_handler['handler'](button)

    class Axis:

        """A single analogue axis on the SixAxis controller"""

        def __init__(
            self,
            name,
            invert=False,
            dead_zone=0.0,
            hot_zone=0.0,
            ):
            self.name = name
            self.center = 0.5
            self.max = 0.9
            self.min = 0.1
            self.value = 0.5
            self.invert = invert
            self.dead_zone = dead_zone
            self.hot_zone = hot_zone

        def corrected_value(self):
            """
                Get a center-compensated, scaled, value for the axis, taking any dead-zone into account. The value will
                scale from 0.0 at the edge of the dead-zone to 1.0 (positive) or -1.0 (negative) at the extreme position of
                the controller or the edge of the hot zone, if defined as other than 1.0. The axis will auto-calibrate for
                maximum value, initially it will behave as if the highest possible value from the hardware is 0.9 in each
                direction, and will expand this as higher values are observed. This is scaled by this function and should
                always return 1.0 or -1.0 at the extreme ends of the axis.

                :return: a float value, negative to the left or down and ranging from -1.0 to 1.0
                """

            high_range = self.max - self.center
            high_start = self.center + self.dead_zone * high_range
            high_end = self.max - self.hot_zone * high_range

            low_range = self.center - self.min
            low_start = self.center - self.dead_zone * low_range
            low_end = self.min + self.hot_zone * low_range

            if self.value > high_start:
                if self.value > high_end:
                    result = 1.0
                else:
                    result = (self.value - high_start) / (high_end
                            - high_start)
            elif self.value < low_start:
                if self.value < low_end:
                    result = -1.0
                else:
                    result = (self.value - low_start) / (low_start
                            - low_end)
            else:
                result = 0

            if not self.invert:
                return result
            else:
                return -result

        def _reset(self):
            """
                Reset calibration (max, min and center values) for this axis specifically. Not generally needed, you can just
                call the reset method on the SixAxis instance.

                :internal:
                """

            self.center = 0.5
            self.max = 0.9
            self.min = 0.1

        def _set(self, new_value):
            """
                Set a new value, called from within the SixAxis class when parsing the event queue.

                :param new_value: the raw value from the joystick hardware
                :internal:
                """

            self.value = new_value
            if new_value > self.max:
                self.max = new_value
            elif new_value < self.min:
                self.min = new_value
        
        def _get(self):
            return self.value


if __name__ == '__main__':
    from control_proc import SixAxis
    import time

    controller = SixAxis(dead_zone=0.0, hot_zone=0.0, connect=True)


    def handler(button):
        print ('Button! {}'.format(button))


    current_milli_time = lambda : int(round(time.time() * 1000))
    last_time = current_milli_time()
    
    
    while 1:              
        now = current_milli_time()
        if now > last_time + 100:
            last_time = now   
