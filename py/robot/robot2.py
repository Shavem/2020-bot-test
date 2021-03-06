import wpilib
import ctre
import magicbot
# import navx
import wpilib.drive
# from enum import IntEnum
from wpilib import Solenoid, DoubleSolenoid
from wpilib.drive import DifferentialDrive


CONTROLLER_LEFT = wpilib.XboxController.Hand.kLeftHand
CONTROLLER_RIGHT = wpilib.XboxController.Hand.kRightHand

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        self.value = DoubleSolenoid.Value.kForward
        self.outin = DoubleSolenoid.Value.kForward

        self.drive_controller = wpilib.XboxController(0)

        # drivetrain
        self.drivetrain_left_motor_master = ctre.WPI_TalonFX(1)
        self.drivetrain_left_motor_slave = ctre.WPI_TalonFX(2)
        self.drivetrain_left_motor_slave2 = ctre.WPI_TalonFX(3)
        self.drivetrain_right_motor_master = ctre.WPI_TalonFX(4)
        self.drivetrain_right_motor_slave = ctre.WPI_TalonFX(5)
        self.drivetrain_right_motor_slave2 = ctre.WPI_TalonFX(6)
        self.left = wpilib.SpeedControllerGroup(
            self.drivetrain_left_motor_master, self.drivetrain_left_motor_slave, self.drivetrain_left_motor_slave2
        )
        self.right = wpilib.SpeedControllerGroup(
            self.drivetrain_right_motor_master, self.drivetrain_right_motor_slave, self.drivetrain_right_motor_slave2
        )
        self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)
        self.drive.setExpiration(0.1)

        self.shifter_shiftsolenoid = wpilib.Solenoid(0)

        self.shift_toggle = True

        # shooter
        # self.hood_solenoid = wpilib.DoubleSolenoid(4,5)
        self.shooter_motor = ctre.WPI_TalonFX(21)
        self.shooter_motor_slave = ctre.WPI_TalonFX(20)

        # intake
        self.intake_roller_motor = ctre.WPI_TalonSRX(10)
        # self.intake_arm_solenoid = wpilib.DoubleSolenoid(2,3)

        # feed
        self.tower_feed_motor_master = ctre.WPI_TalonSRX(9)
        self.tower_feed_motor_slave = ctre.WPI_TalonSRX(11)

        # tower
        self.tower_motor = ctre.WPI_TalonSRX(12)

        # climb
        self.climb_master = ctre.WPI_TalonSRX(8)
        self.climb_slave = ctre.WPI_TalonSRX(13)

    def teleopInit(self):
        """Executed at the start of teleop mode"""
        self.drive.setSafetyEnabled(False)

    def teleopPeriodic(self):
        """Runs the motors with tank steering"""
        angle = self.drive_controller.getX(CONTROLLER_RIGHT)
        speed = self.drive_controller.getY(CONTROLLER_LEFT)
        if (abs(angle) > 0.05 or abs(speed) > 0.05):
            self.drive.arcadeDrive(speed, -angle, True)
        else:
            self.drive.arcadeDrive(0, 0, True)
        # shifter
        if self.drive_controller.getBButtonReleased():
            self.shifter_shiftsolenoid.set(self.shift_toggle)
            if self.shift_toggle:
                self.shift_toggle = False
            else:
                self.shift_toggle = True
            print(self.shift_toggle)

        # intake/feed
        if self.drive_controller.getBumper(CONTROLLER_RIGHT):
            self.intake_roller_motor.set(-0.9)
            self.tower_feed_motor_master.set(0.3)
            self.tower_feed_motor_slave.set(0.3)
        elif self.drive_controller.getAButton():
            self.intake_roller_motor.set(0.9)
            self.tower_feed_motor_master.set(-0.4)
            self.tower_feed_motor_slave.set(-0.4)
        else:
            self.intake_roller_motor.stopMotor()
            self.tower_feed_motor_master.stopMotor()
            self.tower_feed_motor_slave.stopMotor()

        # climb/shooter

        if self.drive_controller.getStartButton():
            self.shooter_motor.set(0.25)
            self.shooter_motor_slave.set(-0.25)
            self.climb_master.set(-0.8)
            self.climb_slave.set(-0.8)
        elif self.drive_controller.getBackButton():
            self.shooter_motor.set(-0.25)
            self.shooter_motor_slave.set(0.25)
            self.climb_master.set(0.6)
            self.climb_slave.set(0.6)
        elif self.drive_controller.getTriggerAxis(CONTROLLER_RIGHT) > 0.75:
            # self.shooter.run_shooter(0.95)
            self.shooter_motor.set(-0.9)
            self.shooter_motor_slave.set(0.9)
        elif self.drive_controller.getTriggerAxis(CONTROLLER_RIGHT) > 0.3:
            # self.shooter.run_shooter(0.5)
            self.shooter_motor.set(-0.5)
            self.shooter_motor_slave.set(0.5)
        else:
            self.shooter_motor.set(0)
            self.shooter_motor_slave.set(0)
            self.climb_master.stopMotor()
            self.climb_slave.stopMotor()

        if self.drive_controller.getTriggerAxis(CONTROLLER_LEFT) > 0.2:
            self.tower_motor.set(-self.drive_controller.getTriggerAxis(CONTROLLER_LEFT))
        elif self.drive_controller.getBumper(CONTROLLER_LEFT):
            self.tower_motor.set(0.5)
        else:
            self.tower_motor.set(0)


if __name__ == "__main__":
    wpilib.run(MyRobot)