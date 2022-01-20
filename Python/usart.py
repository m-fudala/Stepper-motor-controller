import serial
from pySerialTransfer import pySerialTransfer as Transfer


def get_ports():
    ports = serial.tools.list_ports.comports()

    return ports


class SerialLink:
    def __init__(self, port):
        link = Transfer.SerialTransfer(port, baud=1000000, restrict_ports=False)
        link.open()
        self.link = link

    def terminate_link(self):
        self.link.close()

    def send_message(self, message):
        try:
            message_size = self.link.tx_obj(message)
            self.link.send(message_size)

            while not self.link.available():
                if self.link.status < 0:
                    if self.link.status == Transfer.CRC_ERROR:
                        print('ERROR: CRC_ERROR')
                    elif self.link.status == Transfer.PAYLOAD_ERROR:
                        print('ERROR: PAYLOAD_ERROR')
                    elif self.link.status == Transfer.STOP_BYTE_ERROR:
                        print('ERROR: STOP_BYTE_ERROR')
                    else:
                        print('ERROR: {}'.format(self.link.status))

            print('\nSent: {}'.format(message))

        except:
            return

    def send_settings(self, settings):
        try:
            settings_size = self.link.tx_obj(settings)
            self.link.send(settings_size)
        except:
            return

    def receive_message(self):
        rec_message_ = self.link.rx_obj(obj_type=str, obj_byte_size=2, start_pos=0)

        print("Feedback: " + rec_message_)

    def receive_encoder_message(self, channel_z_used):
        while True:
            if self.link.available():
                rec_message_ = self.link.rx_obj(obj_type=str, obj_byte_size=10, start_pos=0)
                print("Received message: " + rec_message_)

                if len(rec_message_) < 4:
                    pass

                negative = False

                if rec_message_[0] == '-':
                    rec_message_ = '0' + rec_message_[1:]
                    negative = True

                impulses = rec_message_[0:7].lstrip('0')

                if not impulses:
                    impulses = 0
                else:
                    if impulses.isdigit():
                        impulses = int(impulses)
                    else:
                        return

                    if negative:
                        impulses = -impulses

                if channel_z_used:
                    negative_z = False

                    if rec_message_[8] == '-':
                        rec_message_[8] = rec_message_[0:7] + '0' + rec_message_[8:]
                        negative_z = True

                    z_impulses = rec_message_[8:11].lstrip('0')

                    if not z_impulses:
                        z_impulses = 0
                    else:
                        if z_impulses.isdigit():
                            z_impulses = int(z_impulses)
                        else:
                            return

                        if negative_z:
                            z_impulses = -z_impulses

                    print("Encoder: " + str(impulses) + '(' + str(z_impulses) + ')')

                    return impulses, z_impulses

                else:
                    print("Encoder: " + str(impulses))

                    return impulses
