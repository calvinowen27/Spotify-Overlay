from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from spotipy import *
import io
import base64
import time
from urllib.request import urlopen
import requests
import keyboard
import threading
from multiprocessing import Process
import time
from OutlinedLabel import OutlinedLabel
from test import testLabel
from ctypes import *
from win32gui import *

APP = QApplication(sys.argv)

WINDOW_WIDTH = 750
WINDOW_HEIGHT = 500
CLIENT_ID = open('data/SpotifyLogin.txt').read().split()[0]
CLIENT_SECRET = open('data/SpotifyLogin.txt').read().split()[1]
REFRESH_RATE = 10
QUIT_BUTTON_SIZE = 35
APP_CONTROL_BUTTON_SIZE = 40
CONTROL_BUTTON_SIZE = 75
ALBUM_COVER_SIZE = 150
LR_SPACING = 5
CONTROL_SPACING = 0
TEXT_SPACING = 5
SONG_CONTROL_SPACING = 10
TITLE_WIDTH = 400
TITLE_HEIGHT = 75
ARTISTS_WIDTH = 400
ARTISTS_HEIGHT = 60
TITLE_CHARS_PER_LINE = 35
ARTISTS_CHARS_PER_LINE = 50
XPOS = 0
YPOS = 1000

CURR_TRACK_INFO = None
CURR_TRACK_NAME = ''
CURR_TRACK_ARTISTS = ''

PREV_TRACK_INFO = None

WINDOW = None

QUIT = False

SP = None


class MainWindow(QMainWindow):
	def __init__(self, sp):
		super().__init__()

		global SP
		SP = sp

		self.setWindowTitle("Spotify Overlay")

		#Buttons
		previous_button = QPushButton()
		previous_button.clicked.connect(self.prev_click)

		previous_button.setStyleSheet("border-image : url(icons/left.png);")

		skip_button = QPushButton()
		skip_button.clicked.connect(self.next_click)

		skip_button.setStyleSheet("border-image : url(icons/right.png);")

		play_button = QPushButton()
		play_button.setCheckable(True)
		play_button.clicked.connect(self.play_click)
		if CURR_TRACK_INFO is not None:
			paused = not CURR_TRACK_INFO['is_playing']
		else:
			paused = True
		if paused:
			play_button.setChecked(True)
			play_button.setStyleSheet("border-image : url(icons/play.png);")
		else:
			play_button.setChecked(False)
			play_button.setStyleSheet("border-image : url(icons/pause.png);")

		quit_button = QPushButton()
		quit_button.clicked.connect(self.end)
		quit_button.setStyleSheet("border-image : url(icons/x.png);")

		minimize_button = QPushButton()
		minimize_button.clicked.connect(self.showMinimized)
		minimize_button.setStyleSheet("border-image : url(icons/-.png);")

		lock_button = QPushButton()
		lock_button.setCheckable(True)
		lock_button.setChecked(True)
		lock_button.clicked.connect(self.lock_click)
		lock_button.setStyleSheet("border-image : url(icons/locked.png);")

		toggle_mouse_button = QPushButton()
		toggle_mouse_button.setCheckable(True)
		toggle_mouse_button.setChecked(True)
		toggle_mouse_button.clicked.connect(self.mouse_icon_click)
		toggle_mouse_button.setStyleSheet("border-image : url(icons/mouse.png);")

		visible_button = QPushButton()
		visible_button.setCheckable(True)
		visible_button.setChecked(True)
		visible_button.clicked.connect(self.visible_click)
		visible_button.setStyleSheet("border-image : url(icons/visible.png);")

		#Song info
		title_label = OutlinedLabel("Song Title")
		title_label.setFont(QFont('Proxima Nova', 10))
		title_label.setScaledOutlineMode(False)
		title_label.setOutlineThickness(2)
		title_label.setWordWrap(True)

		artist_label = OutlinedLabel("Artist")
		artist_label.setBrush(QBrush(QColor(190, 190, 190, 255)))
		artist_label.setFont(QFont('Proxima Nova', 8))
		artist_label.setFixedSize(QSize(ARTISTS_WIDTH, ARTISTS_HEIGHT))
		artist_label.setScaledOutlineMode(False)
		artist_label.setOutlineThickness(2)
		artist_label.setWordWrap(True)

		#Album cover
		album_cover_label = QLabel("Album Cover")
		album_cover_label.setScaledContents(True)
		album_cover_label.setStyleSheet('border: 5px solid black;')

		main_layout = QVBoxLayout()

		app_control_layout = QHBoxLayout()
		app_control_layout.addWidget(visible_button)
		app_control_layout.addWidget(toggle_mouse_button)
		app_control_layout.addWidget(lock_button)

		window_control_temp = QHBoxLayout()
		window_control_temp.addWidget(minimize_button)
		window_control_temp.addWidget(quit_button)
		window_control_layout = QGridLayout()
		window_control_layout.addLayout(window_control_temp, 0, 1)
		window_control_layout.setColumnStretch(0, 1)
		window_control_layout.setRowStretch(1, 1)

		song_info_layout = QVBoxLayout()
		song_info_layout.addWidget(title_label)
		song_info_layout.addWidget(artist_label)

		left_layout = QVBoxLayout()
		left_layout.addLayout(app_control_layout)
		left_layout.addWidget(album_cover_label)

		right_layout = QVBoxLayout()
		right_layout.addLayout(window_control_layout)
		right_layout.addLayout(song_info_layout)

		lr_combined_layout = QHBoxLayout()
		lr_combined_layout.setSpacing(LR_SPACING)
		lr_combined_layout.addLayout(left_layout)
		lr_combined_layout.addLayout(right_layout)

		control_layout = QHBoxLayout()
		control_layout.setSpacing(CONTROL_SPACING)
		control_layout.addWidget(previous_button)
		control_layout.addWidget(play_button)
		control_layout.addWidget(skip_button)

		self.window_layout = QVBoxLayout()
		self.window_layout.addLayout(lr_combined_layout)
		self.window_layout.addLayout(control_layout)

		layout_widget = QWidget()
		layout_widget.setLayout(self.window_layout)
		self.layout_widget = layout_widget

		#Setting content sizes
		previous_button.setFixedSize(QSize(CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE))
		skip_button.setFixedSize(QSize(CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE))
		play_button.setFixedSize(QSize(CONTROL_BUTTON_SIZE, CONTROL_BUTTON_SIZE))
		quit_button.setFixedSize(QSize(QUIT_BUTTON_SIZE, QUIT_BUTTON_SIZE))
		minimize_button.setFixedSize(QSize(QUIT_BUTTON_SIZE, QUIT_BUTTON_SIZE))
		lock_button.setFixedSize(QSize(APP_CONTROL_BUTTON_SIZE, APP_CONTROL_BUTTON_SIZE))
		toggle_mouse_button.setFixedSize(QSize(APP_CONTROL_BUTTON_SIZE, APP_CONTROL_BUTTON_SIZE))
		visible_button.setFixedSize(QSize(APP_CONTROL_BUTTON_SIZE, APP_CONTROL_BUTTON_SIZE))
		title_label.setFixedSize(QSize(TITLE_WIDTH, TITLE_HEIGHT))
		
		album_cover_label.setFixedSize(QSize(ALBUM_COVER_SIZE, ALBUM_COVER_SIZE))

		#self.show()

		sp_retain = self.sizePolicy()
		sp_retain.setRetainSizeWhenHidden(True)
		self.setSizePolicy(sp_retain)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setStyleSheet('background-color: black;')

		self.previous_button = previous_button
		self.skip_button = skip_button
		self.play_button = play_button
		self.quit_button = quit_button
		self.minimize_button = minimize_button
		self.lock_button = lock_button
		self.toggle_mouse_button = toggle_mouse_button
		self.visible_button = visible_button
		self.title_label = title_label
		self.artist_label = artist_label
		self.album_cover_label = album_cover_label
		self.sp = sp
		self.paused = paused
		self.locked = True
		self.mouse_enabled = True
		self.visible = True
		self.drag = False

		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setCentralWidget(self.layout_widget)
		self.move(XPOS, YPOS)
		self.oldPos = self.pos()
		self.defaultWindowFlags = self.windowFlags()

		if CURR_TRACK_INFO is not None:
			self.update_spotify_info()

		self.timer = QTimer(self)
		self.timer.setSingleShot(False)
		self.timer.setInterval(REFRESH_RATE)
		self.timer.timeout.connect(self.update_window)
		self.timer.start()


	def next_click(self):
		if self.mouse_enabled:
			self.next_song()

	def next_song(self):
		if CURR_TRACK_INFO is not None:
			self.sp.next_track()

	def prev_click(self):
		if self.mouse_enabled:
			self.prev_song()

	def prev_song(self):
		if CURR_TRACK_INFO is not None:
			self.sp.previous_track()

	def play_click(self):
		if self.mouse_enabled:
			self.toggle_play(not self.paused)

	def toggle_play(self, paused):
		if CURR_TRACK_INFO is not None:
			if paused:
				self.sp.pause_playback()
				self.play_button.setStyleSheet("border-image : url(icons/play.png);")
			else:
				self.sp.start_playback()
				self.play_button.setStyleSheet("border-image : url(icons/pause.png);")

		self.paused = paused

	def lock_click(self, locked):
		if self.mouse_enabled:
			self.toggle_lock(locked)

	def toggle_lock(self, locked):
		self.locked = locked
		if self.locked:
			self.lock_button.setStyleSheet("border-image : url(icons/locked.png);")
		else:
			self.lock_button.setStyleSheet("border-image : url(icons/unlocked.png);")

	def mouse_icon_click(self, mouse_enabled):
		print(mouse_enabled)
		if self.mouse_enabled:
			self.toggle_mouse(mouse_enabled)

	def toggle_mouse(self, mouse_enabled):
		self.mouse_enabled = mouse_enabled
		if self.mouse_enabled:
			self.toggle_mouse_button.setStyleSheet("border-image : url(icons/nomouse.png);")
			self.setCursor(Qt.BlankCursor)
		else:
			self.toggle_mouse_button.setStyleSheet("border-image : url(icons/mouse.png);")
		self.unsetCursor()

	def visible_click(self, visible):
		if self.mouse_enabled:
			self.toggle_visible(visible)

	def toggle_visible(self, visible):
		self.visible = visible
		if self.visible:
			self.setStyleSheet('background-color: black;')
			self.visible_button.setStyleSheet("border-image : url(icons/visible.png);")
		else:
			self.setStyleSheet('background-color: rgba(128, 128, 128, 0);')
			self.visible_button.setStyleSheet("border-image : url(icons/invisible.png);")

	def get_album_art(self, url):
		image = QImage()
		image.loadFromData(requests.get(url).content)

		im = QPixmap(image)
		im.scaled(ALBUM_COVER_SIZE, ALBUM_COVER_SIZE)
		self.album_cover_label.setPixmap(im)
		self.album_cover_label.show()

	def place_control_key_labels(self):
		for label in self.control_key_labels:
			label.move(label.mapToParent(QPoint(int((label.parentWidget().width() / 2) - label.width() / 2), 30)))

	def update_spotify_info(self):
		global CURR_TRACK_NAME
		global CURR_TRACK_ARTISTS
		global CURR_TRACK_INFO

		try:
			artists = [artist['name'] for artist in CURR_TRACK_INFO['item']['artists']]
			track_name = CURR_TRACK_INFO['item']['name'].split()
		except:
			artists = []
			track_name = []

		CURR_TRACK_NAME = ''
		chars = 0
		for word in track_name:
			#if 'feat.' in word.lower() or 'with' in word.lower() or 'ft.' in word.lower():
				#break
			
			if word != track_name[-1]:
				word += ' '
			if chars < TITLE_CHARS_PER_LINE - len(word):
				CURR_TRACK_NAME += word
				chars += len(word)
			else:
				CURR_TRACK_NAME += '\n'
				CURR_TRACK_NAME += word
				chars = len(word)

		CURR_TRACK_ARTISTS = ''
		chars = 0
		for artist in artists:
			if artist != artists[-1]:
				if chars + len(artist) + 2 <= ARTISTS_CHARS_PER_LINE:
					CURR_TRACK_ARTISTS += artist + ', '
					chars += len(artist) + 2
				elif chars + len(artist) + 1 <= ARTISTS_CHARS_PER_LINE:
					CURR_TRACK_ARTISTS += artist + ','
					chars += len(artist) + 1
				else:
					CURR_TRACK_ARTISTS += '\n' + artist + ', '
					chars = len(artist)
			else:
				if chars + len(artist) <= ARTISTS_CHARS_PER_LINE:
					CURR_TRACK_ARTISTS += artist
				else:
					CURR_TRACK_ARTISTS += '\n' + artist

	def update_window(self):
		global CURR_TRACK_INFO
		global PREV_TRACK_INFO

		try:
			temp = CURR_TRACK_INFO
			CURR_TRACK_INFO = self.sp.current_user_playing_track()
			PREV_TRACK_INFO = temp
		except:
			CURR_TRACK_INFO = None

		if CURR_TRACK_INFO is not None:
			if CURR_TRACK_INFO != PREV_TRACK_INFO:
				self.update_spotify_info()
				self.title_label.setText(CURR_TRACK_NAME)
				self.artist_label.setText(CURR_TRACK_ARTISTS)
				try:
					album_cover_url = CURR_TRACK_INFO['item']['album']['images'][0]['url']
					self.get_album_art(album_cover_url)
					self.paused = not CURR_TRACK_INFO['is_playing']
				except:
					pass

			if self.paused:
				self.play_button.setChecked(True)
				self.play_button.setStyleSheet("border-image : url(icons/play.png);")
			else:
				self.play_button.setChecked(False)
				self.play_button.setStyleSheet("border-image : url(icons/pause.png);")

			if self.locked:
				self.lock_button.setChecked(True)
				self.lock_button.setStyleSheet("border-image : url(icons/locked.png);")
			else:
				self.lock_button.setChecked(False)
				self.lock_button.setStyleSheet("border-image : url(icons/unlocked.png);")

			if self.mouse_enabled:
				self.toggle_mouse_button.setChecked(True)
				self.toggle_mouse_button.setStyleSheet("border-image : url(icons/mouse.png);")
				self.unsetCursor()
			else:
				self.toggle_mouse_button.setChecked(False)
				self.toggle_mouse_button.setStyleSheet("border-image : url(icons/nomouse.png);")
				self.setCursor(Qt.BlankCursor)

			if self.visible:
				self.visible_button.setChecked(True)
				self.visible_button.setStyleSheet("border-image : url(icons/visible.png);")
			else:
				self.visible_button.setChecked(False)
				self.visible_button.setStyleSheet("border-image : url(icons/invisible.png);")

	def end(self):
		global QUIT
		QUIT = True
		APP.exit(0)

	def mousePressEvent(self, event):
		if self.mouse_enabled:
			if not self.locked:
				self.drag = True
				self.oldPos = event.globalPos()

	def mouseReleaseEvent(self, event):
		if self.mouse_enabled:
			if not self.locked:
				self.drag = False

	def mouseMoveEvent(self, event):
		if self.mouse_enabled:
			if not self.locked:
				delta = QPoint(event.globalPos() - self.oldPos)
				self.move(self.x() + delta.x(), self.y() + delta.y())
				self.oldPos = event.globalPos()


def window_setup(sp):
	global WINDOW

	window = MainWindow(sp)
	WINDOW = window

	window.show()

	APP.exec()


def spotify_setup():
	global CURR_TRACK_INFO
	
	try:
		scopes = ['user-read-currently-playing', 'streaming']
		auth_manager = SpotifyOAuth(scope=scopes, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='https://localhost/')
		sp = Spotify(auth_manager=auth_manager)
	except:
		ccm = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
		sp = Spotify(client_credentials_manager=ccm)

	CURR_TRACK_INFO = sp.current_user_playing_track()

	return sp

def read_keyboard():
	import keyboard

	hllDll = WinDLL("User32.dll")

	F7_states = [0, 0]
	F8_states = [0, 0]
	F9_states = [0, 0]
	F10_states = [0, 0]
	F11_states = [0, 0]
	F12_states = [0, 0]

	count = 0

	while True:
		if QUIT:
			break

		scroll_lock = bool(hllDll.GetKeyState(0x91))

		F7_states = update_key_states(F7_states, 0x76, hllDll)
		F8_states = update_key_states(F8_states, 0x77, hllDll)
		F9_states = update_key_states(F9_states, 0x78, hllDll)
		F10_states = update_key_states(F10_states, 0x79, hllDll)
		F11_states = update_key_states(F11_states, 0x7A, hllDll)
		F12_states = update_key_states(F12_states, 0x7B, hllDll)

		if WINDOW is not None:
			if not WINDOW.mouse_enabled:
				if scroll_lock:
					if F7_states[1] != F7_states[0]:
						WINDOW.toggle_visible(not WINDOW.visible)
					if F8_states[1] != F8_states[0]:
						WINDOW.toggle_mouse(not WINDOW.mouse_enabled)
					if F9_states[1] != F9_states[0]:
						WINDOW.toggle_play(not WINDOW.paused)
					if F10_states[1] != F10_states[0]:
						WINDOW.end()
					if F11_states[1] != F11_states[0]:
						WINDOW.prev_song()
					if F12_states[1] != F12_states[0]:
						WINDOW.next_song()
			else:
				if WINDOW.drag:
					WINDOW.update()

def update_key_states(states, keycode, hllDll):
	key = hllDll.GetKeyState(keycode)
	states[0] = states[1]
	if key >= 1:
		key = 1
	states[1] = key
	return states


def main():
	sp = spotify_setup()

	key_thread = threading.Thread(target=read_keyboard)
	key_thread.start()

	window_setup(sp)

	key_thread.join()
	exit()

if __name__ == '__main__':
	main()