from __future__ import annotations

import sys
from typing import Callable

import cv2
from PyQt5.QtCore import (
    QRect,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import QGuiApplication, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class Gui:
    def __init__(self, path: str, seconds: int) -> None:
        self.q_app = QApplication([])
        self.q_app.setStyle("Fusion")
        screen = QGuiApplication.screens()[0]
        availableGeometry = screen.availableGeometry()
        self.primary_width = availableGeometry.width()
        self.primary_height = availableGeometry.height() - 30
        self.gui_window = GuiWindow(self, path, seconds)

    def exit_app(self) -> None:
        self.q_app.quit()
        sys.exit()


class GuiWindow(QWidget):
    def __init__(self, gui: Gui, path: str, seconds: int) -> None:
        super().__init__()
        self.gui = gui
        self.window_width: int = gui.primary_width
        self.window_height: int = gui.primary_height
        rect = QRect(0, 0, self.window_width, self.window_height)
        self.setGeometry(rect)
        self.setFixedSize(QSize(self.window_width, self.window_height))
        self.layout: Layout = VideoLayout(self, 50, 212)
        self.setLayout(self.layout)
        self.show()
        self.layout.start_video(path, seconds)


class Label(QLabel):
    def __init__(
        self,
        text: str,
        color: str,
        right_aligment: bool,
        bold: bool,
        description: str,
        background: str,
    ) -> None:
        super().__init__(text)
        style = "QLabel {color: " + color
        if bold:
            style += "; font-weight: bold"
        if background == "":
            style += "}"
        else:
            style += "; background-color: " + background + "}"
        if description != "":
            style += "QToolTip {background-color: white; color: black; font-size: 12px}"
            self.setToolTip(description)
        self.setStyleSheet(style)
        if right_aligment:
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


class PushButton(QPushButton):
    def __init__(
        self, text: str, color: str, action: Callable, description: str
    ) -> None:
        super().__init__(text)
        style = "QPushButton {background-color: " + color + "; font-weight: bold}"
        if description != "":
            style += "QToolTip {background-color: white; color: black; font-size: 12px}"
            self.setToolTip(description)
        self.setStyleSheet(style)
        self.pressed.connect(action)


class Layout(QGridLayout):
    def __init__(
        self,
        window: GuiWindow,
        rows: int = 50,
        columns: int = 212,
    ) -> None:
        super().__init__()
        self.window = window

        self.width = window.window_width
        self.height = window.window_height
        self.num_of_columns = columns
        self.num_of_rows = rows

        self.column_width = int(self.width / self.num_of_columns)
        self.row_height = int(self.height / self.num_of_rows)

        self.setHorizontalSpacing(0)
        self.setVerticalSpacing(0)

        for i in range(self.num_of_columns):
            self.setColumnMinimumWidth(i, self.column_width)

        for i in range(self.num_of_rows):
            self.setRowMinimumHeight(i, self.row_height)

        self.data_from_video_change_requested.connect(self.exit)

    def exit(self) -> None:
        self.window.gui.exit_app()

    def create_and_add_label(
        self,
        text: str,
        row: int,
        column: int,
        width: int,
        height: int,
        color: str,
        right_aligment: bool = False,
        bold: bool = True,
        description: str = "",
        background: str = "",
    ) -> Label:

        label = Label(text, color, right_aligment, bold, description, background)
        label.setFixedSize(width * self.column_width, height * self.row_height)
        self.addWidget(label, row, column, height, width)
        return label

    def create_and_add_button(
        self,
        text: str,
        row: int,
        column: int,
        width: int,
        height: int,
        action: Callable,
        description: str,
        color: str = "lightgray",
    ) -> PushButton:

        button = PushButton(text, color, action, description)
        button.setFixedSize(width * self.column_width, height * self.row_height)
        self.addWidget(button, row, column, height, width)
        return button


class VideoLayout(Layout):
    data_from_video_change_requested = pyqtSignal(str)

    def __init__(self, window: GuiWindow, rows: int, columns: int) -> None:
        super().__init__(window, rows=rows, columns=columns)
        self.draw()

    def draw(self) -> None:
        self.video_label = QLabel()
        self.addWidget(self.video_label, 0, 0, 46, 210)

        self.speed = 1
        self.speed_text = "Speed: x" + str(self.speed)

        self.create_and_add_button(
            "CLOSE", 0, 185, 20, 2, self.close, "Close the video"
        )
        self.create_and_add_button(
            "PLAY/PAUSE", 8, 178, 20, 2, self.play_pause, "Play or pause the video"
        )
        self.speed_label = self.create_and_add_label(
            self.speed_text, 11, 183, 15, 2, "black"
        )
        self.create_and_add_button(
            "SPEED x 2",
            14,
            190,
            20,
            2,
            self.double_speed,
            "Double the video speed",
        )
        self.create_and_add_button(
            "SPEED / 2",
            14,
            165,
            20,
            2,
            self.half_speed,
            "Halve the video speed",
        )
        self.create_and_add_button(
            "1 FRAME >",
            17,
            190,
            20,
            2,
            self.forward_frame,
            "Skip forward 1 frame",
        )
        self.create_and_add_button(
            "< 1 FRAME",
            17,
            165,
            20,
            2,
            self.backward_frame,
            "Skip backward 1 frame",
        )
        self.create_and_add_button(
            "10 SECONDS >>",
            20,
            190,
            20,
            2,
            self.forward_ten_seconds,
            "Skip forward 10 seconds",
        )
        self.create_and_add_button(
            "<< 10 SECONDS",
            20,
            165,
            20,
            2,
            self.backward_ten_seconds,
            "Skip backward 10 seconds",
        )
        self.create_and_add_button(
            "5 MINUTES >>>",
            23,
            190,
            20,
            2,
            self.forward_five_minutes,
            "Skip forward 5 minutes",
        )
        self.create_and_add_button(
            "<<< 5 MINUTES",
            23,
            165,
            20,
            2,
            self.backward_five_minutes,
            "Skip backward 5 minutes",
        )

    def start_video(self, path: str, seconds: int) -> None:
        try:
            self.cap = cv2.VideoCapture(path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.millisecs = int(1000.0 / self.fps / self.speed)

            if seconds > 0:
                frames_to_skip = int(self.fps * seconds)
                new_frame_position = min(frames_to_skip, self.total_frames - 60)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)

            self.timer = QTimer()
            self.timer.setTimerType(Qt.PreciseTimer)
            self.timer.timeout.connect(self.next_frame_slot)
            self.timer.start(self.millisecs)
        except Exception:
            pass

    def play_pause(self) -> None:
        try:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start()
        except Exception:
            pass

    def double_speed(self) -> None:
        try:
            if self.speed < 4:
                self.speed *= 2
            self.millisecs = int(1000.0 / self.fps / self.speed)
            self.speed_text = "Speed: x" + str(self.speed)
            self.timer.setInterval(self.millisecs)
            self.speed_label.setText(self.speed_text)
        except Exception:
            pass

    def half_speed(self) -> None:
        try:
            if self.speed > 0.06:
                self.speed / 2
            self.millisecs = int(1000.0 / self.fps / self.speed)
            self.speed_text = "Speed: x" + str(self.speed)
            self.timer.setInterval(self.millisecs)
            self.speed_label.setText(self.speed_text)
        except Exception:
            pass

    def forward_frame(self) -> None:
        try:
            if self.timer.isActive():
                self.timer.stop()
            self.next_frame_slot()
        except Exception:
            pass

    def backward_frame(self) -> None:
        try:
            if self.timer.isActive():
                self.timer.stop()
            if self.cap.isOpened():
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                new_frame_position = max(0, current_frame - 2)
                print(current_frame, new_frame_position)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)
                self.next_frame_slot()
        except Exception:
            pass

    def forward_ten_seconds(self) -> None:
        try:
            if self.cap.isOpened():
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                frames_to_skip = int(self.fps * 10)
                new_frame_position = min(
                    current_frame + frames_to_skip, self.total_frames - 1
                )
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)
                self.next_frame_slot()
        except Exception:
            pass

    def backward_ten_seconds(self) -> None:
        try:
            if self.cap.isOpened():
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                frames_to_skip = int(self.fps * 10)
                new_frame_position = max(0, current_frame - frames_to_skip)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)
                self.next_frame_slot()
        except Exception:
            pass

    def forward_five_minutes(self) -> None:
        try:
            if self.cap.isOpened():
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                frames_to_skip = int(self.fps * 60 * 5)
                new_frame_position = min(
                    current_frame + frames_to_skip, self.total_frames - 1
                )
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)
                self.next_frame_slot()
        except Exception:
            pass

    def backward_five_minutes(self) -> None:
        try:
            if self.cap.isOpened():
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                frames_to_skip = int(self.fps * 60 * 5)
                new_frame_position = max(0, current_frame - frames_to_skip)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_position)
                self.next_frame_slot()
        except Exception:
            pass

    def stop_button_clicked(self) -> None:
        try:
            self.timer.stop()
            self.cap.release()
        except Exception:
            pass

    def close(self) -> None:
        self.stop_button_clicked()
        self.data_from_video_change_requested.emit("")

    def next_frame_slot(self) -> None:
        ret, frame = self.cap.read()
        if ret:
            img = QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                frame.strides[0],
                QImage.Format_BGR888,
            )

            pix = QPixmap.fromImage(img)
            self.video_label.setPixmap(pix)

    def update_data(self) -> None:
        pass


try:
    path = sys.argv[1]
except Exception:
    raise Exception("Please provide a video file path")

gui = Gui(path, 0)
gui.q_app.exec()
