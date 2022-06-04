from pyfirmata import ArduinoMega, util, SERVO, PWM
from time import sleep, time
import constants as const
import control_proc
from control_proc import SixAxis

class BlackSpot:
    def __init__(self, h_cam_servo1, v_cam_servo2):
        self.board = ArduinoMega("/dev/ttyACM1")
        self.h_cam_axis = h_cam_servo1
        self.v_cam_axis = v_cam_servo2
        self.camera = BlackSpot.Camera(self.h_cam_axis, self.v_cam_axis)
        self.center_camera()
        self.controller = SixAxis()
        self.set_pins()
        
    def lock_camera(self, r):
        self.set_camera_center(self.controller.get_axes()[0].value, self.controller.get_axes()[1].value)
        self.center_camera()
        
    def run(self):
        self.controller.register_button_handler(self.lock_camera, 14)
        while True:
            while not self.controller.is_connected():
                try:
                    self.controller.connect()
                    sleep(1)
                    print("Controller Connected!")
                except IOError:
                    print("Connect Controller!")
                    sleep(1)
                    
            if (self.controller.get_axes()[1].value > 0.3 or self.controller.get_axes()[1].value < -0.3 or
                self.controller.get_axes()[0].value > 0.1 or self.controller.get_axes()[0].value < -0.1):
                self.move_camera(self.controller.get_axes()[0].value, self.controller.get_axes()[1].value)
            else:
                self.center_camera()
                
                  
        
    def change_camera_servos(self, h_cam_servo1, v_cam_servo2):
        self.camera._set_servos(h_cam_servo1, v_cam_servo2)
        
    def set_pins(self):
        self.board.digital[const.SERVO2].mode = SERVO
        self.board.digital[const.SERVO3].mode = SERVO
        self.board.digital[const.RIGHT_PWM].mode = PWM
        self.board.digital[const.LEFT_PWM].mode = PWM
        
    def move_camera(self, h_val, v_val):
        self.board.digital[const.SERVO2].write(self.camera._set_horiz_angle(h_val))
        self.board.digital[const.SERVO3].write(self.camera._set_vert_angle(v_val))
    
    def center_camera(self):
        center = self.camera._get_center()
        self.move_camera(float(center[0]), float(center[1]))
    
    def set_camera_center(self, h_val, v_val):
        center = self.camera._set_center(h_val, v_val)
        return center
                
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
            
    def __str__(self):
        return "camera vertical: {}, camera horizontal: {}".format(self.camera._get_center()[0], self.camera._get_center()[1])
    
    class Camera:
        
        def __init__(self, servo_horizontal, servo_vertical):
            self.max_val = 0.8
            self.servo_hor = servo_horizontal
            self.servo_ver = servo_vertical
            self.center = (const.CENTER, const.CENTER)
            self.h_angle = self.center[0]
            self.v_angle = self.center[1]
            
        def _set_servos(self, servo_horizontal, servo_vertical):
            self.servo_hor = servo_horizontal
            self.servo_ver = servo_vertical
            
        def _get_axes(self):
            return (h_angle, v_angle)
        
        def _get_center(self):
            return self.center
        
        def _set_horiz_angle(self, val):
            if val >= -self.max_val and val <= self.max_val:
                self.h_angle = 90 - (val * 90)
            return self.h_angle
        
        def _set_vert_angle(self, val):
            if val >= -self.max_val and val <= self.max_val:
                self.v_angle = 90 - (val * 90)
            return self.v_angle
        
        def _set_center(self, h_val, v_val):
            self.center = (h_val, v_val)

if __name__ == '__main__':
    
    def lock_camera(r):
        print("button clicked {}".format(r))
        
        
    r = BlackSpot(const.SERVO2, const.SERVO3)
 

    r.run()
    
            
            
             
    
