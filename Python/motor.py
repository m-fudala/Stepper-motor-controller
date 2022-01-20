from usart import SerialLink
import time


class StepperMotor:
    def __init__(self, port, steps_per_rev):
        self.steps_per_rev = steps_per_rev
        self.send = SerialLink(port)

        if port != "COM99":
            settings = "1"

            self.send.send_message(settings)
            self.send.receive_message()
            time.sleep(0.5)

        print(f'Nowa klasa --- port:{port}, kroki: {steps_per_rev}')

    def end_link(self):
        self.send.terminate_link()

    def reset(self):
        self.send.send_message('r')
        self.send.receive_message()

    @staticmethod
    def set_speed(steps_count, speed, if_rpm_mode):
        if if_rpm_mode:
            delay = int(60000000 / (speed * steps_count))   # w mikrosekundach
        else:
            delay = speed

        delay = str(delay).zfill(5)

        return delay

    @staticmethod
    def check_if_positive(steps):
        if steps > 0:
            return '1'
        else:
            return '0'

    def start_fs(self, steps, speed, if_rpm_mode):
        steps_count = 1 * self.steps_per_rev
        delay = self.set_speed(steps_count, speed, if_rpm_mode)

        message = "1" + str(abs(steps)).zfill(5) + self.check_if_positive(steps) + delay
        self.send.send_message(message)
        self.send.receive_message()
        time.sleep(0.5)

        return True

    def start_hs(self, steps, speed, if_rpm_mode):
        steps_count = 2 * self.steps_per_rev
        delay = self.set_speed(steps_count, speed, if_rpm_mode)

        message = "2" + str(abs(steps)).zfill(5) + self.check_if_positive(steps) + delay
        self.send.send_message(message)
        self.send.receive_message()
        time.sleep(0.5)

        return True

    def start_ms(self, scaler, steps, speed, if_rpm_mode):
        steps_count = (2 ** scaler) * self.steps_per_rev

        delay = self.set_speed(steps_count, speed, if_rpm_mode)

        message = "3" + str(abs(steps)).zfill(5) + self.check_if_positive(steps) + delay + str(scaler).zfill(2)
        self.send.send_message(message)
        self.send.receive_message()
        time.sleep(0.5)

        return True

    def send_new_setting(self, new_setting):
        self.send.send_message(new_setting)
        self.send.receive_message()

    def get_encoder_ticks(self, channel_z_used):
        return self.send.receive_encoder_message(channel_z_used)
