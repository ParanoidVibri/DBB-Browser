import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QAction, QToolBar, QMenu, QMenuBar, QFileDialog, QMessageBox, QPushButton, QProgressBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QKeySequence

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enhanced QTWebEngine Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize bookmarks list
        self.bookmarks = []

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create the navigation bar
        self.nav_bar = QToolBar("Navigation")
        self.addToolBar(self.nav_bar)

        # Back and forward buttons
        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back")
        back_btn.setShortcut(QKeySequence.Back)
        back_btn.triggered.connect(self.back)
        self.nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Forward")
        forward_btn.setShortcut(QKeySequence.Forward)
        forward_btn.triggered.connect(self.forward)
        self.nav_bar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload")
        reload_btn.setShortcut(QKeySequence.Refresh)
        reload_btn.triggered.connect(self.reload)
        self.nav_bar.addAction(reload_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.setStatusTip("New Tab")
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.nav_bar.addAction(new_tab_btn)

        # Address bar and search button
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_url_from_bar)
        self.nav_bar.addWidget(self.address_bar)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.navigate_to_url_from_bar)
        self.nav_bar.addWidget(search_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)
        layout.addWidget(self.progress_bar)

        # Bookmark actions
        bookmark_btn = QAction("Bookmark", self)
        bookmark_btn.setStatusTip("Bookmark This Page")
        bookmark_btn.triggered.connect(self.add_bookmark)
        self.nav_bar.addAction(bookmark_btn)

        # Menu Bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")

        # Load bookmarks from file
        load_action = QAction("Load Bookmarks", self)
        load_action.setStatusTip("Load bookmarks from file")
        load_action.triggered.connect(self.load_bookmarks)
        file_menu.addAction(load_action)

        # Save bookmarks to file
        save_action = QAction("Save Bookmarks", self)
        save_action.setStatusTip("Save bookmarks to file")
        save_action.triggered.connect(self.save_bookmarks)
        file_menu.addAction(save_action)

        # Exit application
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Bookmarks menu
        self.bookmark_menu = QMenu("Bookmarks", self)
        self.menu_bar.addMenu(self.bookmark_menu)
        self.bookmark_menu.aboutToShow.connect(self.update_bookmark_menu)

        # Set the initial URL
        self.add_new_tab()
        self.navigate_to_url("http://www.google.com")

    def add_new_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        browser = QWebEngineView()
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)
        layout.addWidget(browser)
        tab.setLayout(layout)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        self.update_address_bar()
        import sys
        app = QApplication(sys.argv)
        tab_widget = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()

        tab_widget.addTab(tab1, "Tab 1")
        tab_widget.addTab(tab2, "Tab 2")
        tab_widget.setStyleSheet("QTabBar::tab { border-radius: 10px; }")
        tab_widget.show()

    def update_address_bar(self):
        current_browser = self.current_browser()
        if current_browser:
            url = current_browser.url().toString()
            self.address_bar.setText(url)

    def navigate_to_url(self, url=None):
        if url is None:
            url = self.address_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        current_browser = self.current_browser()
        if current_browser:
            print(f"Navigating to URL: {url}")  # Debugging line
            current_browser.setUrl(QUrl(url))

    def navigate_to_url_from_bar(self):
        self.navigate_to_url()

    def back(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.back()

    def forward(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.forward()

    def reload(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.reload()

    def add_bookmark(self):
        current_browser = self.current_browser()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            if (url, title) not in self.bookmarks:
                self.bookmarks.append((url, title))
                self.update_bookmark_menu()

    def update_bookmark_menu(self):
        self.bookmark_menu.clear()
        for url, title in self.bookmarks:
            bookmark_action = QAction(title, self)
            bookmark_action.setData(url)
            bookmark_action.triggered.connect(self.navigate_bookmark)
            self.bookmark_menu.addAction(bookmark_action)

    def navigate_bookmark(self):
        action = self.sender()
        url = action.data()
        self.navigate_to_url(url)

    def load_bookmarks(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Bookmark File", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "r") as file:
                    self.bookmarks = json.load(file)
                    self.update_bookmark_menu()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load bookmarks: {e}")

    def save_bookmarks(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Bookmark File", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, "w") as file:
                    json.dump(self.bookmarks, file, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save bookmarks: {e}")

    def current_browser(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            return self.tabs.widget(current_index).findChild(QWebEngineView)
        return None

    def on_load_started(self):
        print("Page load started...")  # Debugging line
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def on_load_progress(self, progress):
        print(f"Page load progress: {progress}%")  # Debugging line
        self.progress_bar.setValue(progress)

    def on_load_finished(self, success):
        print(f"Page load finished, success: {success}")  # Debugging line
        if success:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(0)
        # Hide progress bar after loading is finished
        self.progress_bar.hide()

# Quick Bar
class ToolbarExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Website Toolbar')

        widget = QWidget()
        layout = QVBoxLayout()
        
        google_button = QPushButton('Google')
        facebook_button = QPushButton('Facebook')
        discord_button = QPushButton('Discord')
        add_button = QPushButton('Add')
        
        google_button.clicked.connect(self.www.google.com)
        facebook_button.clicked.connect(self.www.facebook.com)
        discord_button.clicked.connect(self.www.discord.com/app)
        add_button.clicked.connect(self.add_website)

        layout.addWidget(google_button)
        layout.addWidget(facebook_button)
        layout.addWidget(discord_button)
        layout.addWidget(add_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_google(self):
        pass

    def open_facebook(self):
        pass

    def open_discord(self):
        pass

    def add_website(self):
        pass

# Picture In Picture mode
class VideoPlayerExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Video Player')

        main_layout = QVBoxLayout()

        self.main_label = QLabel('Main Video Player')
        main_layout.addWidget(self.main_label)

        self.active_video_playing = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_video_playing)
        self.timer.start(1000)  # Check every 1 second

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def check_video_playing(self):
        self.active_video_playing = not self.active_video_playing

        if self.active_video_playing:
            self.show_picture_in_picture()

    def show_picture_in_picture(self):
        self.pip_dialog = QDialog(self)
        self.pip_dialog.setWindowTitle('Picture-in-Picture View')
        self.pip_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)

        pip_layout = QVBoxLayout()

        self.pip_label = QLabel('Picture-in-Picture Window')
        pip_layout.addWidget(self.pip_label)

        close_pip_button = QPushButton('Close Picture-in-Picture')
        close_pip_button.clicked.connect(self.pip_dialog.close)
        pip_layout.addWidget(close_pip_button)

        self.pip_dialog.setLayout(pip_layout)
        self.pip_dialog.show()
        
    def pause_resume_video(self):
        if self.pause_button.text() == 'Pause':
            self.pause_button.setText('Resume')
        else:
            self.pause_button.setText('Pause')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
