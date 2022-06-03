from pyfirmata import ArduinoMega, util, SERVO, PWM
from time import sleep, time
import constants as const
import control_proc
class BlackSpot:
    
    def __init__(self):
        self.board = ArduinoMega("/dev/ttyACM0")
        self.set_pins()
        self.rotate_servo(const.SERVO3, const.SERVO_CENTER)
        self.rotate_servo(const.SERVO2, const.SERVO_CENTER)
        
    def set_pins(self):
        self.board.digital[const.SERVO2].mode = SERVO
        self.board.digital[const.SERVO3].mode = SERVO
        self.board.digital[const.RIGHT_PWM].mode = PWM
        self.board.digital[const.LEFT_PWM].mode = PWM
        
    def rotate_servo(self, servo, angle):
        self.board.digital[servo].write(angle)

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

    def left_track(self, button):
        print(button)
        if button == 13:
            self.board.digital[const.LEFT_DIGI1].write(const.HIGH)
            self.board.digital[const.LEFT_DIGI2].write(const.LOW)
            self.board.digital[const.LEFT_PWM].write(const.HIGH)
        elif button == 11:
            self.board.digital[const.LEFT_DIGI1].write(const.LOW)
            self.board.digital[const.LEFT_DIGI2].write(const.HIGH)
            self.board.digital[const.LEFT_PWM].write(const.HIGH)
        else:
            self.board.digital[const.RIGHT_PWM].write(const.LOW)
            self.board.digital[const.LEFT_PWM].write(const.LOW)



if __name__ == '__main__':
    from control_proc import SixAxis
    import time
    
    def handler(button):
        print ('Button! {}'.format(button))
        
    r = BlackSpot()
    controller = SixAxis(dead_zone=0.0, hot_zone=0.0)
            
    current_milli_time = lambda : int(round(time.time() * 1000))
    last_time = current_milli_time()
    
    while True:
        while not controller.is_connected():
            try:
                controller.connect()
                print("Controller Connected!")
            except IOError:
                print("Connect Controller!")
                sleep(1)
            
        if (controller.get_axes()[1].value > 0.1 or controller.get_axes()[1].value < -0.1 or controller.get_axes()[0].value > 0.1 or controller.get_axes()[0].value < -0.1):
            r.rotate_servo(const.SERVO2, 90 - (controller.get_axes()[0].value * const.SERVO_CENTER))
            r.rotate_servo(const.SERVO3, 90 - (controller.get_axes()[1].value * const.SERVO_CENTER))
        else:
            r.rotate_servo(const.SERVO2, 90)
            r.rotate_servo(const.SERVO3, 90)
            controller.reset_axis_calibration
            
    