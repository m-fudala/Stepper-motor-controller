import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6 import QtGui
from PyQt6 import uic
import time

from motor import StepperMotor
from usart import get_ports


class WindowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.setWindowIcon(QtGui.QIcon('engine.ico'))
        self.mainTabWidget.currentChanged.connect(self.change_button_visibility)
        self.buttonRefreshPorts.clicked.connect(self.refresh_ports)
        self.checkBoxEncoder.stateChanged.connect(self.set_encoder_active)
        self.checkBoxEncoderZ.stateChanged.connect(self.set_channel_z_active)
        self.buttonConfirmSettings.clicked.connect(self.confirm_settings)
        self.buttonEncoderImpulses.clicked.connect(self.confirm_encoder_settings)

        self.checkBoxFullStep.stateChanged.connect(self.set_full_step_mode)
        self.checkBoxHalfStep.stateChanged.connect(self.set_half_step_mode)
        self.checkBoxMicroStep.stateChanged.connect(self.set_micro_step_mode)

        self.startButton.clicked.connect(self.set_movement)
        self.buttonReset.clicked.connect(self.reset)

        self.buttonAddMovement.clicked.connect(self.add_movement_to_trajectory)
        self.buttonClearTrajectories.clicked.connect(self.clear_trajectories)
        self.mainTabWidget.currentChanged.connect(self.list_trajectories)

        self.movement_list = []
        self.steps_per_rev = 0

        self.widgetButtons.hide()
        self.widgetReset.hide()
        self.mainTabWidget.setTabEnabled(1, False)
        self.mainTabWidget.setTabEnabled(2, False)
        self.mainTabWidget.setCurrentIndex(0)

        self.checkBoxEncoder.setEnabled(False)
        self.widgetEncoder.hide()
        self.widgetEncoderShowcase.hide()

        self.checkBoxFullStep.setChecked(True)
        self.checkBoxHalfStep.setChecked(False)
        self.checkBoxMicroStep.setChecked(False)

        self.motor = StepperMotor("COM99", 200)
        self.motor.end_link()

        self.ports = []
        self.refresh_ports()
        self.mode = 1

        self.motor_set = False
        self.encoder_used = False
        self.encoder_pulses_scaler = 0.0
        self.channel_z_used = False
        self.encoder_ticks_received = True

        self.tableWidgetTrajectories.resizeColumnsToContents()
        self.tableWidgetTrajectories.setColumnWidth(0, 100)

    def refresh_ports(self):
        self.ports = get_ports()

        self.comboBoxPortSelection.clear()

        arduinos_count = 0

        for index, description in enumerate(self.ports):
            if "Arduino" in str(description):
                self.comboBoxPortSelection.insertItem(index, self.ports[index].description)
                arduinos_count += 1

        if arduinos_count == 0:
            self.comboBoxPortSelection.insertItem(index, "Brak podłączonego Arduino.")

    def confirm_settings(self):
        if self.motor_set:
            self.reset()

        steps_per_rev = self.plainTextEditStepsPR.toPlainText()

        if steps_per_rev.isdigit():
            steps_per_rev = int(steps_per_rev)

            if steps_per_rev < 1:
                self.plainTextEditStepsPR.clear()
                self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)

                return

        else:
            self.plainTextEditStepsPR.clear()
            self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)

            return

        self.steps_per_rev = steps_per_rev

        self.motor = StepperMotor(self.ports[self.comboBoxPortSelection.currentIndex()].name, self.steps_per_rev)
        self.motor_set = True
        self.mainTabWidget.setTabEnabled(1, True)
        self.mainTabWidget.setTabEnabled(2, True)
        self.widgetReset.show()
        self.checkBoxEncoder.setEnabled(True)

    def set_encoder_active(self):
        if not self.motor_set:
            return

        if self.checkBoxEncoder.isChecked():
            self.encoder_used = True
            self.widgetEncoder.show()
            self.widgetEncoderShowcase.show()
            self.plainTextEditEncoder.setPlainText("0 kroków")

            if self.motor_set:
                self.motor.send_new_setting("e1")
        else:
            self.encoder_used = False
            self.widgetEncoder.hide()
            self.widgetEncoderShowcase.hide()

            if self.motor_set:
                self.motor.send_new_setting("e0")

    def set_channel_z_active(self):
        if self.checkBoxEncoderZ.isChecked():
            self.channel_z_used = True

            if self.motor_set:
                self.motor.send_new_setting("z1")
        else:
            self.channel_z_used = False

            if self.motor_set:
                self.motor.send_new_setting("z0")

    def confirm_encoder_settings(self):
        if self.encoder_used:
            pulses_per_rev = self.plainTextEditEncoderPulsesPR.toPlainText()

            if pulses_per_rev.isdigit():
                pulses_per_rev = int(pulses_per_rev)

                if pulses_per_rev < 1:
                    self.plainTextEditEncoderPulsesPR.clear()
                    self.statusBar().showMessage('Podaj właściwą wartość impulsów.', 2000)

                    return

            else:
                self.plainTextEditEncoderPulsesPR.clear()
                self.statusBar().showMessage('Podaj właściwą wartość impulsów.', 2000)

                return

            self.encoder_pulses_scaler = self.steps_per_rev / pulses_per_rev

    def change_button_visibility(self):
        if self.mainTabWidget.currentIndex() != 0:
            self.widgetButtons.show()
        else:
            self.widgetButtons.hide()

    def set_full_step_mode(self):
        self.check_if_mode_chosen()

        if self.checkBoxFullStep.isChecked():
            self.checkBoxHalfStep.setChecked(False)
            self.checkBoxMicroStep.setChecked(False)

            self.mode = 1

    def set_half_step_mode(self):
        self.check_if_mode_chosen()

        if self.checkBoxHalfStep.isChecked():
            self.checkBoxFullStep.setChecked(False)
            self.checkBoxMicroStep.setChecked(False)

            self.mode = 2

    def set_micro_step_mode(self):
        self.check_if_mode_chosen()

        if self.checkBoxMicroStep.isChecked():
            self.checkBoxFullStep.setChecked(False)
            self.checkBoxHalfStep.setChecked(False)

            self.mode = 3

    def check_if_mode_chosen(self):
        if not self.checkBoxFullStep.isChecked() and not self.checkBoxHalfStep.isChecked() and not self.checkBoxMicroStep.isChecked():
            self.checkBoxFullStep.setChecked(True)
            self.set_full_step_mode()

    def add_movement_to_trajectory(self):
        if self.mode == 1:
            steps = self.spinBoxStepsFull.value()

            if steps == 0:
                self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                return

            movement_settings = (self.mode, 0, steps, self.spinBoxSpeedFull.value())

        elif self.mode == 2:
            steps = self.spinBoxStepsHalf.value()

            if steps == 0:
                self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                return

            movement_settings = (self.mode, 1, steps, self.spinBoxSpeedHalf.value())

        elif self.mode == 3:
            steps = self.spinBoxStepsMicro.value()

            if steps == 0:
                self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                return

            movement_settings = (self.mode, int(self.comboBoxMicroScaler.currentIndex()), steps, self.spinBoxSpeedMicro.value())

        self.movement_list.append(movement_settings)
        self.statusBar().showMessage('Dodano ruch.', 2000)

    def set_movement(self):
        if self.encoder_used and self.encoder_pulses_scaler == 0.0:
            self.statusBar().showMessage('Podaj wartość impulsów enkodera przed rozpoczęciem ruchu.', 2000)
            return

        if self.mainTabWidget.currentIndex() == 1:
            mode = self.mode

            if mode == 1:
                scaler = 0
                steps = self.spinBoxStepsFull.value()

                if steps == 0:
                    self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                    return

                speed = self.spinBoxSpeedFull.value()

            elif mode == 2:
                scaler = 0
                steps = self.spinBoxStepsHalf.value()

                if steps == 0:
                    self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                    return

                speed = self.spinBoxSpeedHalf.value()

            elif mode == 3:
                scaler = int(self.comboBoxMicroScaler.currentIndex())
                steps = self.spinBoxStepsMicro.value()

                if steps == 0:
                    self.statusBar().showMessage('Podaj właściwą wartość kroków.', 2000)
                    return

                speed = self.spinBoxSpeedMicro.value()

            else:
                return

            self.start_movement(1, self.movement_list, mode, scaler, steps, speed)

        elif self.mainTabWidget.currentIndex() == 2:
            self.start_movement(2, self.movement_list, 0, 0, 0, 0)

    def start_movement(self, current_index, movement_list, mode, scaler, steps, speed):
        self.movement_worker = MovementWorker(self.motor, self.encoder_used, self.channel_z_used, current_index, movement_list, mode, scaler, steps, speed)
        self.movement_worker.start()
        self.movement_worker.encoder_ticks_collected.connect(self.show_encoder_data)

    def show_encoder_data(self, encoder_ticks, z_channel_ticks):
        self.encoder_ticks_received = True

        if self.channel_z_used:
            encoder_steps = encoder_ticks * self.encoder_pulses_scaler
            self.plainTextEditEncoder.setPlainText(str(encoder_steps) + " kroków (" + str(z_channel_ticks) + " obrotów)")

        else:
            encoder_steps = encoder_ticks * self.encoder_pulses_scaler

            self.plainTextEditEncoder.setPlainText(str(encoder_steps) + " kroków")

    def list_trajectories(self):
        types_dict = {1: "pełnokrokowy", 2: "półkrokowy", 3: "mikrokrokowy"}

        if self.mainTabWidget.currentIndex() == 2:
            self.tableWidgetTrajectories.setRowCount(0)
            self.tableWidgetTrajectories.setRowCount(len(self.movement_list))

            for i, row in enumerate(self.movement_list):
                self.tableWidgetTrajectories.setItem(i, 0, QTableWidgetItem(types_dict[row[0]]))
                self.tableWidgetTrajectories.setItem(i, 1, QTableWidgetItem(str(2 ** row[1])))
                self.tableWidgetTrajectories.setItem(i, 2, QTableWidgetItem(str(row[2])))
                self.tableWidgetTrajectories.setItem(i, 3, QTableWidgetItem(str(row[3])))

            self.tableWidgetTrajectories.resizeRowsToContents()

    def clear_trajectories(self):
        self.movement_list.clear()
        self.tableWidgetTrajectories.setRowCount(0)

    def reset(self):
        self.motor.reset()

        self.motor_set = False
        self.checkBoxEncoder.setEnabled(False)
        self.encoder_used = False
        self.channel_z_used = False
        self.widgetEncoder.hide()
        self.checkBoxEncoder.setChecked(False)
        self.checkBoxEncoderZ.setChecked(False)
        self.mainTabWidget.setTabEnabled(1, False)
        self.mainTabWidget.setTabEnabled(2, False)
        self.encoder_pulses_scaler = 0.0
        self.plainTextEditEncoderPulsesPR.clear()

    def closeEvent(self, event):
        if self.motor_set:
            self.reset()

        self.motor.end_link()


class MovementWorker(QThread):
    encoder_ticks_collected = pyqtSignal(int, int)

    def __init__(self, motor, encoder_used, channel_z_used, current_index, movement_list, mode, scaler, steps, speed):
        super().__init__()
        self.motor = motor
        self.encoder_used = encoder_used
        self.channel_z_used = channel_z_used
        self.current_index = current_index
        self.movement_list = movement_list

        self.mode = mode
        self.scaler = scaler
        self.steps = steps
        self.speed = speed

    def run(self):
        if self.current_index == 1:
            if self.mode == 1:
                movement_started = self.motor.start_fs(self.steps, self.speed, True)

            elif self.mode == 2:
                movement_started = self.motor.start_hs(self.steps, self.speed, True)

            elif self.mode == 3:
                movement_started = self.motor.start_ms(self.scaler, self.steps, self.speed, True)

            else:
                return

            if movement_started and self.encoder_used:
                self.data_worker = DataGetterWorker(self.motor, self.channel_z_used)
                self.data_worker.encoder_ticks_collected.connect(self.send_encoder_data)
                self.data_worker.start()

        elif self.current_index == 2:
            for i, row in enumerate(self.movement_list):
                mode = row[0]
                scaler = row[1]
                steps = row[2]
                speed = row[3]

                if mode == 1:
                    movement_started = self.motor.start_fs(steps, speed, True)

                elif mode == 2:
                    movement_started = self.motor.start_hs(steps, speed, True)

                elif mode == 3:
                    movement_started = self.motor.start_ms(scaler, steps, speed, True)

                else:
                    return

                if movement_started and self.encoder_used:
                    self.data_worker = DataGetterWorker(self.motor, self.channel_z_used)
                    self.data_worker.encoder_ticks_collected.connect(self.send_encoder_data)
                    self.data_worker.start()

                    time.sleep(0.2)

    def send_encoder_data(self, encoder_ticks, channel_z_ticks):
        self.encoder_ticks_collected.emit(encoder_ticks, channel_z_ticks)


class DataGetterWorker(QThread):
    encoder_ticks_collected = pyqtSignal(int, int)

    def __init__(self, motor, channel_z_used):
        super().__init__()
        self.motor = motor
        self.channel_z_used = channel_z_used

    def run(self):
        if self.channel_z_used:
            encoder_ticks, z_channel_ticks = self.motor.get_encoder_ticks(self.channel_z_used)

        else:
            encoder_ticks = self.motor.get_encoder_ticks(self.channel_z_used)
            z_channel_ticks = -1

        self.encoder_ticks_collected.emit(encoder_ticks, z_channel_ticks)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = WindowApp()
    window.show()

    sys.exit(app.exec())
