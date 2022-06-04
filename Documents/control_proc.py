from asyncore import file_dispatcher, loop
from threading import Thread

try:
    from evdev import InputDevice, list_devices, ecodes
except ImportError:
    print ('Did not import device')

class SixAxis:
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

    def __init__(self, connect=False):
        self.buttons_pressed = 0
        self.button_handlers = []
        self._stop_function = None
        self.axes = [SixAxis.Axis('left_x'), SixAxis.Axis('left_y'),
                     SixAxis.Axis('right_x'), SixAxis.Axis('right_y')]
        if connect:
            self.connect()

    def is_connected(self):
        if self._stop_function:
            return True
        else:
            return False

    def connect(self):
        if self._stop_function:
            return False
        for device in [InputDevice(fn) for fn in list_devices()]:
            if 'PLAYSTATION(R)3 Controller' in device.name:
                parent = self

                class InputDeviceDispatcher(file_dispatcher):

                    def __init__(self):
                        self.device = device
                        file_dispatcher.__init__(self, device)

                    def recv(self, ign=None):
                        return self.device.read()

                    def handle_read(self):
                        for event in self.recv():
                            parent.handle_event(event)

                    def handle_error(self):
                        print("Controller Disconnected")
                        parent.disconnect()
                        self.close()

                class AsyncLoop(Thread):

                    def __init__(self, channel):
                        Thread.__init__(self, name='InputDispatchThread', daemon=True)
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
        if self._stop_function:
            self._stop_function()
            self._stop_function = None

    def reset_axis_calibration(self):
        # Resets axis to 0.0 for all axes
        for axis in self.axes:
            axis._reset()

    def register_button_handler(self, button_handler, buttons):
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

    def handle_event(self, event):
        if event.type == ecodes.EV_ABS:
            value = float(event.value) / 127
            if event.code == 0:
                # Left stick, X axis
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
                            
    def __str__(self):
        return 'x1={}, y1={}, x2={}, y2={}'.format(self.axes[0].value,
                self.axes[1].value,
                self.axes[2].value,
                self.axes[3].value)
    
    def get_axes(self):
        return self.axes
    
    class Axis:
        def __init__(self, name, invert=False):
            self.name = name
            self.max = 0.9
            self.min = 0.1
            self.value = 0.0
            self.invert = invert

        def _set(self, new_value):
            self.value = new_value
            if new_value > self.max:
                self.max = new_value
            elif new_value < self.min:
                self.min = new_value
                
        def _reset(self):
            self.max = 0.9
            self.min = 0.1
            self.value = 0.0
            
        def _get(self):
            return self.value


   
