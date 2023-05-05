import sys
import time
import os
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, 
                             QPushButton, QHBoxLayout, QFormLayout, QMessageBox)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from undetected_chromedriver import Chrome
from undetected_chromedriver.options import ChromeOptions
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QEvent
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')
credentials_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.txt')


class AutobumperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.logged_in = False
        self.bump_timer = None
        self.autobump_running = False

        self.hover_sound = QSoundEffect()
        self.hover_sound.setSource(QUrl.fromLocalFile("./resources/sounds/hover_sound.wav"))


    def initUI(self):
        self.setWindowTitle('Demonico`s autobumper - version 1')

        # font
        font = QFont("Arial", 12)
        self.setFont(font)

        # widget style
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(50, 50, 50, 255), stop:1 rgba(25, 25, 25, 255));
                color: white;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(60, 60, 60, 255), stop:1 rgba(35, 35, 35, 255));
                border: 1px solid white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(70, 70, 70, 255), stop:1 rgba(45, 45, 45, 255));
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 80, 80, 255), stop:1 rgba(55, 55, 55, 255));
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 50);
                border: 1px solid white;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        self.form = QFormLayout()
        self.username_field = QLineEdit()
        self.form.addRow('Username:', self.username_field)
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.form.addRow('Password:', self.password_field)
        self.thread_url_field = QLineEdit()
        self.form.addRow('Thread URL:', self.thread_url_field)
        self.interval_field = QLineEdit()
        self.form.addRow('Bump Interval (mins):', self.interval_field)
        self.bump_message_field = QLineEdit()
        self.bump_message_field.setText('Autobump')
        self.form.addRow('Bump Message:', self.bump_message_field)

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        self.start_button = QPushButton('Start Autobump')
        self.start_button.clicked.connect(self.start_autobump)
        self.stop_button = QPushButton('Stop Autobump')
        self.stop_button.clicked.connect(self.stop_autobump)
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.close_app)
        self.restart_button = QPushButton('Restart')
        self.restart_button.clicked.connect(self.restart_app)
        self.help_button = QPushButton('Help')
        self.help_button.clicked.connect(self.show_help_message)
        
        # Set icons for buttons
        self.login_button.setIcon(QIcon("./resources/icons/login_icon.png"))
        self.start_button.setIcon(QIcon("./resources/icons/start_icon.png"))
        self.stop_button.setIcon(QIcon("./resources/icons/stop_icon.png"))
        self.exit_button.setIcon(QIcon("./resources/icons/exit_icon.png"))
        self.restart_button.setIcon(QIcon("./resources/icons/restart_icon.png"))
        self.help_button.setIcon(QIcon("./resources/icons/help_icon.png"))

        # Connect hover sound to buttons
        self.login_button.installEventFilter(self)
        self.start_button.installEventFilter(self)
        self.stop_button.installEventFilter(self)
        self.exit_button.installEventFilter(self)
        self.restart_button.installEventFilter(self)
        self.help_button.installEventFilter(self)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.exit_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.help_button)

        self.status_label = QLabel('Status: Not Running')
        
        def eventFilter(self, source, event):
            if event.type() == QEvent.HoverEnter and source in (self.login_button, self.start_button, self.stop_button,
                                                                self.exit_button, self.restart_button, self.help_button):
                self.hover_sound.play()
            return super().eventFilter(source, event)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.load_credentials()

    def restart_app(self):
        if self.logged_in:
            self.browser.quit()

        python = sys.executable
        os.execl(python, python, *sys.argv)

    def show_help_message(self):
        help_msg = QMessageBox(self)
        help_msg.setIcon(QMessageBox.Information)
        help_msg.setWindowTitle("Help")
        help_msg.setText("Instructions:")
        help_msg.setInformativeText("1. Enter your username and password.\n"
                                     "2. Enter the thread URL you want to autobump.\n"
                                     "3. Enter the bump interval (in minutes).\n"
                                     "4. Click the 'Login' button to log in.\n"
                                     "5. Click the 'Start Autobump' button to start autobumping.\n"
                                     "6. Click the 'Stop Autobump' button to stop autobumping.\n"
                                     "7. To restart the application, click the 'Restart' button.")
       
        help_msg.exec_()

    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.browser, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def load_credentials(self):
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    self.username_field.setText(lines[0].strip())
                    self.password_field.setText(lines[1].strip())

    def close_app(self):
        if self.logged_in:
            self.browser.quit()
        self.close()

    def human_typing(self, element, text, delay_range=(50, 150)):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(delay_range[0], delay_range[1]) / 1000)

    def login(self):
        if self.logged_in:
            self.show_help_message()
            return

        username = self.username_field.text()
        password = self.password_field.text()

        if not username or not password:
            self.status_label.setText('Status: Invalid username or password')
            return

        options = ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--remote-debugging-port=9222')

        self.browser = Chrome(executable_path=chromedriver_path, options=options)
        self.browser.get('https://ogusers.gg/login.php')

        try:
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
            user_input = self.browser.find_element(By.NAME, 'username')
            pass_input = self.browser.find_element(By.NAME, 'password')
        except Exception as e:
            self.status_label.setText(f'Status: Failed to find input fields ({e})')
            print(f'Error: {e}')  # Log error to console
            return

        self.human_typing(user_input, username)
        self.human_typing(pass_input, password)
        pass_input.send_keys(Keys.RETURN)
        QTimer.singleShot(2000, self.check_login)

    def check_login(self):
        if 'index' in self.browser.current_url:
            self.logged_in = True
            self.status_label.setText('Status: Logged in')
            self.status_label.setStyleSheet("color: green")
            thread_url = self.thread_url_field.text()
            self.navigate_to_thread(thread_url)
            self.login_button.setDisabled(True)
        else:
            self.status_label.setText('Status: Failed to log in')
            self.status_label.setStyleSheet("color: red")

    def navigate_to_thread(self, thread_url):
        if not self.logged_in:
            self.status_label.setText('Status: Not logged in')
            return

        self.browser.get(thread_url)
        self.wait_for_page_load()

    def post_reply(self, reply_content):
        if not self.logged_in:
            self.status_label.setText('Status: Not logged in')
            return

        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.note-editable[contenteditable="true"]')))
            reply_box = self.browser.find_element(By.CSS_SELECTOR, 'div.note-editable[contenteditable="true"]')
            self.browser.execute_script("arguments[0].innerHTML = '';", reply_box)
            reply_box.click()
            self.human_typing(reply_box, reply_content)
            time.sleep(random.uniform(1, 3))

            WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Reply')]")))
            submit_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Reply')]")

            time.sleep(2)

            submit_button.click()
            self.wait_for_page_load()
        except Exception as e:
            self.status_label.setText(f'Status: Failed to post reply ({e})')
            print(f'Error: {e}')  # Log error to console
            return

    def auto_bump(self):
        thread_url = self.thread_url_field.text()

        if not thread_url:
            self.status_label.setText('Status: Invalid thread URL')
            return

        self.navigate_to_thread(thread_url)
        bump_message = self.bump_message_field.text()
        if not bump_message:
            bump_message = 'Autobump'

        self.post_reply(bump_message)
        interval = int(self.interval_field.text()) * 60
        self.update_status(interval - 1)

    def update_status(self, remaining_time):
        if not self.autobump_running:
            return

        if remaining_time <= 0:
            self.status_label.setText('Status: Thread bumped')
        else:
            self.status_label.setText(f'Status: Autobumping - {remaining_time} seconds until next bump')
            QTimer.singleShot(1000, lambda: self.update_status(remaining_time - 1))

    def start_autobump(self):
        interval_text = self.interval_field.text().strip()

        if not interval_text.isdigit():
            self.status_label.setText('Status: Invalid bump interval')
            return

        interval = int(interval_text)

        self.status_label.setText('Status: Autobumping started')
        self.autobump_running = True

        self.auto_bump()

        interval_ms = interval * 60 * 1000
        self.bump_timer = QTimer(self)
        self.bump_timer.timeout.connect(self.auto_bump)
        self.bump_timer.start(interval_ms)

    def stop_autobump(self):
        if self.bump_timer:
            self.bump_timer.stop()
            self.status_label.setText('Status: Autobumping stopped')
            self.bump_timer = None

        self.autobump_running = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AutobumperApp()
    ex.show()
    sys.exit(app.exec_())

