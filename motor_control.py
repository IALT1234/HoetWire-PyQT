try:
    import RPi.GPIO as GPIO
except ImportError:
    from mock_gpio import MockGPIO
    GPIO = MockGPIO()  # Instantiate the mock GPIO
    
from time import sleep

'''
To map the Header Board Terminal Block Connector numbers to their corresponding GPIO pins 
please refer to https://pinout.xyz/pinout/pwm for the translation.
'''


class MotorConfig:

    #These attributes will keep track of the current coordinates of the motors
    #Ensure the motors are at home at the start of the website
    # -1 indicates the location of the motors are unknown and need to reset
    x_position:float = -1.00
    z_position:float = -1.00

    #This indicates the step sizes the motor should move 
    #200 pulses = 1 millimeter, 100 pulses = 0.5 millimeter 50: 0.25 
    pulse_distance = 200

    #Lets functions know to continue executions or to stop 
    #This variable is handled by app.py 
    running = True 

    # Limit switch GPIO pins
    LIMIT_X = 2
    LIMIT_Z = 3
    # Motor X GPIO pins
    PULSE_X = 17
    DIR_X = 27
    ENABLE_X = 22
    # Motor Z GPIO pins
    PULSE_Z = 23
    DIR_Z = 24
    ENABLE_Z = 25
    #Relay GPIO pins
    RELAY_1 = 20
    RELAY_2 = 19

    '''
    When an instance of this class is created it will automatically set up the GPIO pins of the RPi.
    GPIO INPUT PINS: This pins are meant to be read for their current signal
        [LIMIT_X,LIMIT_Z]: are pins for the X switch and Z switch, respectively. 
            0: The switch is NOT being pressed
            1: The switch is being pressed down
    GPIO OUTPUT PINS: This pins are given a signal of 0 or 1 to be sent to the RPi.
        [PULSE_X, PULSE_Z]: sends a pulse to the motors to move and rotate the corresponding axis. [200 pulses = 1 millimeter]
            0: Stops the motor from moving by not giving it a pulse
            1: Sends pulses to the specific motor
        [DIR_X,DIR_Z]: Sends a signal to indicate the direction the motor should move in 
            DIR_X:
                0: Left on the X motor
                1: Right on the X motor
            DIR_Z:
                0: Up on the Z motor
                1: Down on the Z motor
        [ENABLE_X,ENABLE_Z]: This signals the corresponding motor to turn on or off.
            0: Turns the motors ON to receive power.
            1: Turns the motors OFF         

    '''
    def __init__(self):
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([MotorConfig.LIMIT_X, MotorConfig.LIMIT_Z], GPIO.IN)
        GPIO.setup([MotorConfig.PULSE_X, MotorConfig.DIR_X, MotorConfig.ENABLE_X,
                    MotorConfig.PULSE_Z, MotorConfig.DIR_Z, MotorConfig.ENABLE_Z], GPIO.OUT)
        GPIO.setup([MotorConfig.RELAY_1, MotorConfig.RELAY_2], GPIO.OUT)
        
        return
    
    '''
    This enables or disables the X and Z motors based on the passed argument.
        0: ON
        1: OFF
    
    Args:
        x_enable: Sends the X motor the given signal should be 0 or 1
        z_enable: Sends the Z motor the given signal should be 0 or 1

    '''
    def set_enable(self,x_enable: int, z_enable: int):
        GPIO.output(self.ENABLE_X, x_enable)
        GPIO.output(self.ENABLE_Z, z_enable)
        return 

    '''
    This sends an output signal to the X and Z motor to change direction based on the passed 
    argument.
    
    Args:
        x_dir: Set's the X motor's direction LEFT if 0 or RIGHT if 1
        z_dir: Set's the X motor's direction UP if 0 or DOWN if 1

    '''
    def set_direction(self, x_dir: int, z_dir: int):
        GPIO.output(self.DIR_X, x_dir)
        GPIO.output(self.DIR_Z, z_dir)
        return 

    '''
    This function moves the specified motor in the given direction by a certain number of pulses.
    
    Args:
        axis: Specifies whether to move the 'x' motor or 'z' motor
        direction: Specifies the direction the motor should move in 
        pulses: Specifies the amount of pulses the motor should receive to move a certain distance 

    
    The distance in millimeters the motor successfully moved is then updated for the motors position.
    '''
    def move_motor(self, axis: str, direction: int, pulses: int):
        #Sets up the specified motor
        if axis.lower() == 'x':
            DIR_PIN = self.DIR_X
            PULSE_PIN = self.PULSE_X
            ENABLE_PIN = self.ENABLE_X
            LIMIT_PIN = self.LIMIT_X
        elif axis.lower() == 'z':
            DIR_PIN = self.DIR_Z
            PULSE_PIN = self.PULSE_Z
            ENABLE_PIN = self.ENABLE_Z
            LIMIT_PIN = self.LIMIT_Z

        
        GPIO.output(ENABLE_PIN, 0) #Turns motor on
        sleep(0.1) #Gives the motor enough time to receive power
        pulses = int(pulses) 
        GPIO.output(DIR_PIN, direction)
        for i in range(pulses):
            if self.running and not (GPIO.input(LIMIT_PIN) and direction):
                GPIO.output(PULSE_PIN, 1)
                sleep(0.001)
                GPIO.output(PULSE_PIN, 0)
                sleep(0.001)
            else:
                pulses = i
                break
        if axis.lower() == 'x':
            #If direction is 1 the motors are moving right decreasing the motors position
            self.x_position = self.x_position - pulses/200 if direction else self.x_position + pulses/200 
        else:
            self.z_position = self.z_position - pulses/200 if direction else self.z_position + pulses/200 
        
        return 

    '''
    Takes in the current position of the motor and the desired position the motor should move to.
    This function calculates in what direction the motor should move in and how many pulses
    the motor should receive to get to the final position.

    Args:
        axis: The motor that needs to be moved
        initial_pos: The current position the motor is at.
        final_pos: The desired position the motor should move to.
    
    '''
    
    def move_to_position(self, axis: str, initial_pos: float, final_pos: float):   
        displacement = final_pos - initial_pos
        if displacement != 0:
            direction = 1 if displacement < 0 else 0
            pulses = abs(displacement) * self.pulse_distance
            self.move_motor(axis, direction, pulses)
        return  

    '''
    This function resets the motors (ie homes the motors) by moving the motors towards the 
    switches and stops once the switches have been pressed. 

    Returns:
        The total distance motors moved in millimeters. 

    '''
    def reset(self) -> float: 
        x_reset = False
        z_reset = False
        self.running = True
        
        GPIO.output(self.ENABLE_X, 0)
        GPIO.output(self.DIR_X, 1)
        GPIO.output(self.ENABLE_Z, 0)
        GPIO.output(self.DIR_Z, 1)
        total_x_pulses = 0
        total_z_pulses = 0
        while not(x_reset and z_reset):
            if not self.running:
                self.running = True
                self.x_position -= total_x_pulses/200
                self.z_position -= total_z_pulses/200

                break
            if GPIO.input(self.LIMIT_X): # If the switch is being pressed
                GPIO.output(self.ENABLE_X, 1) #Turn motors off
                x_reset = True
                self.x_position = 0.00
            else:
                self.pulsex(1) # Move motor by 1 pulse
                total_x_pulses += 1

            if GPIO.input(self.LIMIT_Z):
                GPIO.output(self.ENABLE_Z, 1)

                z_reset = True
                self.z_position = 0.0
            else:
                self.pulsez(1)
                total_z_pulses += 1
        self.running = True     
        return 
    
    '''
    This sends a certain amount of pulses to the X motor to make it move.

    Arg:
        pulses: The amount of pulses to be sent to the X motor.
        200 pulses = 1 millimeter in distance
    '''
    def pulsex(self, pulses: int):
        for i in range(pulses):
            GPIO.output(self.PULSE_X, 1)
            sleep(.001)
            GPIO.output(self.PULSE_X, 0)
            sleep(.001)
        return

    '''
    This sends a certain amount of pulses to the Z motor to make it move.

    Arg:
        pulses: The amount of pulses to be sent to the Z motor.
        200 pulses = 1 millimeter in distance
        1 pulse = .005 millimeter
    '''
    def pulsez(self,pulses: int):
        for i in range(pulses):
            GPIO.output(self.PULSE_Z, 1)
            sleep(.001)
            GPIO.output(self.PULSE_Z, 0)
            sleep(.001)
        return
    
    '''
    This function is utilized for the jog-mode page to allow for individual movements of the motors.
    The distant moved is specified by the current value of pulse_distance moving the motor that step size.
    
    Arg:
        button: An integer indicating the desired direction the motor should move in.
            Values should be 0-3 
            0: LEFT on X motor
            1: RIGHT on X motor
            2: UP on Z motor
            3: DOWN on Z motor
    '''
    def joystick(self, button: int):

        if button == 0:
            self.move_motor('x', 0, self.pulse_distance) 
            
        elif button == 1:
            self.move_motor('x', 1, self.pulse_distance) 
     
        elif button == 2:
            self.move_motor('z', 0, self.pulse_distance)

        elif button == 3:
            self.move_motor('z', 1, self.pulse_distance)
        return

    '''
    This function turns the relays connected to the CTAs that power the Hot Wires on or off.

    Args:
        relay: The number of the relay wanting to enable or disable
            Values should be 1 or 2
            1: First relay, CTA, Hot Wire 1
            2: Second relay, CTA, Hot Wire 2
        power: Indicates whether to enable or disable the relay
            Values should be 0 or 1
            0: OFF (ie disable)
            1: ON (ie enable)
    '''   
    def relays(self, relay: int, power:int):

        if relay == 1:
            GPIO.output(self.RELAY_1, power)  
        if relay == 2:
            GPIO.output(self.RELAY_2, power)

        return
    
    def validate_position(self):
        if (self.x_position == -1.0 or self.z_position == -1.0):
            self.reset()
            self.x_position = 0
            self.z_position =0

