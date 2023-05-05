# OGUsers.gg-Auto-Bumper
open source auto bumper for OGUsers.gg

This code is a Python script that creates an automatic thread bumper application for a forum called "ogusers.gg" using PyQt5 for the GUI and Selenium with the undetected_chromedriver package to interact with the website.

1. Import the necessary libraries and set paths for chromedriver and credentials.txt.
2. Create a class called AutobumperApp that inherits from QWidget. This class will represent the main application window.
3. Define the __init__ and initUI methods to set up the user interface, including form fields, buttons, and their corresponding event handlers.
4. Define the eventFilter method to handle hover events on the buttons and play a hover sound.
5. Define the restart_app, show_help_message, wait_for_page_load, load_credentials, and close_app methods to handle various actions like restarting the application, showing help, waiting for a page to load, loading credentials, and closing the app.
6. Define the human_typing method, which simulates human typing by sending characters one by one with random delays between them.
7. Define the login and check_login methods to handle the login process.
8. Define the navigate_to_thread, post_reply, auto_bump, update_status, start_autobump, and stop_autobump methods to handle the process of navigating to a thread, 9. posting a reply, starting the automatic bumping process, updating the status label, and stopping the automatic bumping process.
9. Finally, in the if __name__ == '__main__': block, create an instance of the QApplication, instantiate the AutobumperApp class, show the application window, and start the application event loop.

When run, this script will display a window where users can input their login credentials, a thread URL, a bump interval, and a bump message. Users can then log in, start the autobump process, and stop it as needed. The script will simulate human-like typing to post replies on the given thread URL at the specified interval.
