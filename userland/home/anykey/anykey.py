import adafruit_ssd1306
import board
import busio
import digitalio
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import threading
import time
import traceback
import usb.core
import usb.util

class BonnetDisplay():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.i2c = busio.I2C(board.SCL, board.SDA)
		self.disp = adafruit_ssd1306.SSD1306_I2C(width, height, self.i2c)
		self.disp.fill(0)
		self.disp.show()
		self.image = PIL.Image.new('1', (width, height))
		self.draw = PIL.ImageDraw.Draw(self.image)
		self.clear()

	def clear(self):
		self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

	def show(self):
		self.disp.image(self.image)
		self.disp.show()

class BonnetButtons():
	A = 0x01
	B = 0x02
	LEFT = 0x04
	RIGHT = 0x08
	UP = 0x10
	DOWN = 0x20
	CENTER = 0x40

	def __init__(self):
		self.button_A = digitalio.DigitalInOut(board.D5)
		self.button_A.direction = digitalio.Direction.INPUT
		self.button_A.pull = digitalio.Pull.UP
		self.button_B = digitalio.DigitalInOut(board.D6)
		self.button_B.direction = digitalio.Direction.INPUT
		self.button_B.pull = digitalio.Pull.UP
		self.button_L = digitalio.DigitalInOut(board.D27)
		self.button_L.direction = digitalio.Direction.INPUT
		self.button_L.pull = digitalio.Pull.UP
		self.button_R = digitalio.DigitalInOut(board.D23)
		self.button_R.direction = digitalio.Direction.INPUT
		self.button_R.pull = digitalio.Pull.UP
		self.button_U = digitalio.DigitalInOut(board.D17)
		self.button_U.direction = digitalio.Direction.INPUT
		self.button_U.pull = digitalio.Pull.UP
		self.button_D = digitalio.DigitalInOut(board.D22)
		self.button_D.direction = digitalio.Direction.INPUT
		self.button_D.pull = digitalio.Pull.UP
		self.button_C = digitalio.DigitalInOut(board.D4)
		self.button_C.direction = digitalio.Direction.INPUT
		self.button_C.pull = digitalio.Pull.UP

	def read(self):
		buttons = 0
		if not self.button_A.value:
			buttons |= self.A
		if not self.button_B.value:
			buttons |= self.B
		if not self.button_L.value:
			buttons |= self.LEFT
		if not self.button_R.value:
			buttons |= self.RIGHT
		if not self.button_U.value:
			buttons |= self.UP
		if not self.button_D.value:
			buttons |= self.DOWN
		if not self.button_C.value:
			buttons |= self.CENTER
		return buttons

	def wait_for_release(self):
		time.sleep(0.1)
		while self.read():
			time.sleep(0.1)

CODES_USB = [
	'00', '01 Roll Over', '02 POST Fail', '03 Undefined',
	'04 A a', '05 B b', '06 C c', '07 D d', '08 E e', '09 F f', '0A G g', '0B H h', '0C I i',
	'0D J j', '0E K k', '0F L l', '10 M m', '11 N n', '12 O o', '13 P p', '14 Q q', '15 R r',
	'16 S s', '17 T t', '18 U u', '19 V v', '1A W w', '1B X x', '1C Y y', '1D Z z', '1E ! 1',
	'1F @ 2', '20 # 3', '21 $ 4', '22 % 5', '23 ^ 6', '24 & 7', '25 * 8', '26 ( 9', '27 ) 0',
	'28 Enter', '29 Escape', '2A Backspace', '2B Tab', '2C Space',
	'2D _ -', '2E + =', '2F { [', '30 } ]', '31 ANSI | \\', '32 ISO/JIS | \\',
	'33 : ;', '34 \" \'', '35 ~ `', '36 < ,', '37 > .', '38 ? /', '39 Caps Lock',
	'3A F1', '3B F2', '3C F3', '3D F4', '3E F5', '3F F6', '40 F7', '41 F8', '42 F9',
	'43 F10', '44 F11', '45 F12', '46 PrtSc/SysRq', '47 Scroll Lock', '48 Pause/Break',
	'49 Insert', '4A Home', '4B Page Up', '4C Delete', '4D End', '4E Page Down',
	'4F Arrow Right', '50 Arrow Left', '51 Arrow Down', '52 Arrow Up',
	'53 Num Lock', '54 Numpad /', '55 Numpad *', '56 Numpad -', '57 Numpad +', '58 Numpad Enter',
	'59 Numpad 1/End', '5A Numpad 2/Down', '5B Numpad 3/PgDn', '5C Numpad 4/Left', '5D Numpad 5',
	'5E Numpad 6/Rght', '5F Numpad 7/Home', '60 Numpad 8/Up', '61 Numpad 9/PgUp', '62 Numpad 0/Ins',
	'63 Numpad ./Del', '64 ISO 102nd < >', '65 Context Menu', '66 Power', '67 Numpad = Mac',
	'68 F13', '69 F14', '6A F15', '6B F16', '6C F17', '6D F18',
	'6E F19', '6F F20', '70 F21', '71 F22', '72 F23', '73 F24',
	'74 Open', '75 Help', '76 Props', '77 Front', '78 Stop', '79 Again',
	'7A Undo', '7B Cut', '7C Copy', '7D Paste', '7E Find',
	'7F Mute', '80 Volume Up', '81 Volume Down',
	'82 Locking Caps', '83 Locking NumLk', '84 Locking ScrLk',
	'85 Numpad ,', '86 Numpad = Unix',
	'87 Intl1 _ \\', '88 Intl2 Kana', '89 Intl3 | Yen',
	'8A Intl4 Henkan', '8B Intl5 Muhnkan',
	'8C Intl6', '8D Intl7', '8E Intl8', '8F Intl9',
	'90 Lang1', '91 Lang2', '92 Lang3', '93 Lang4', '94 Lang5',
	'95 Lang6', '96 Lang7', '97 Lang8', '98 Lang9',
	'99 Alt Erase', '9A SysRq', '9B Cancel', '9C Clear', '9D Prior', '9E Return',
	'9F Sep', 'A0 Out', 'A1 Oper', 'A2 Again', 'A3 CrSel', 'A4 ExSel',
	'A5', 'A6', 'A7', 'A8', 'A9', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF',
	'B0 Keypad 00', 'B1 Keypad 000', 'B2 Thousands Sep', 'B3 Decimal Sep',
	'B4 Currency Unit', 'B5 Curr Subunit', 'B6 Keypad (', 'B7 Keypad )',
	'B8 Keypad {', 'B9 Keypad }', 'BA Keypad Tab', 'BB Keypad Bksp',
	'BC Keypad A', 'BD Keypad B', 'BE Keypad C', 'BF Keypad D', 'C0 Keypad E', 'C1 Keypad F',
	'C2 Keypad XOR', 'C3 Keypad ^', 'C4 Keypad %', 'C5 Keypad <', 'C6 Keypad >',
	'C7 Keypad &', 'C8 Keypad &&', 'C9 Keypad |', 'CA Keypad ||', 'CB Keypad :',
	'CC Keypad #', 'CD Keypad Space', 'CE Keypad @', 'CF Keypad !',
	'D0 Keypad MS', 'D1 Keypad MR', 'D2 Keypad MC',
	'D3 Keypad M+', 'D4 Keypad M-', 'D5 Keypad M*', 'D6 Keypad M/',
	'D7 Keypad +/-', 'D8 Keypad Clear', 'D9 Keypad CE',
	'DA Keypad BIN', 'DB Keypad OCT', 'DC Keypad DEC', 'DD Keypad HEX',
	'DE', 'DF',
	'E0 Left Ctrl', 'E1 Left Shift', 'E2 Left Alt', 'E3 Left Meta',
	'E4 Right Ctrl', 'E5 Right Shift', 'E6 Right Alt', 'E7 Right Meta',
	'E8 Play/Pause', 'E9 Stop Track', 'EA Prev Track', 'EB Next Track',
	'EC Eject', 'ED Volume Up', 'EE Volume Down', 'EF Mute',
	'F0 WWW Home', 'F1 WWW Back', 'F2 WWW Forward', 'F3 WWW Stop',
	'F4 WWW Search', 'F5 Scroll Up', 'F6 Scroll Down', 'F7 Edit',
	'F8 Sleep', 'F9 Wake', 'FA Refresh', 'FB Calculator',
	'FC', 'FD', 'FE', 'FF'
]

def isBootKeyboard(device):
	for config in device:
		for iface in config:
			if iface.bInterfaceClass == 3: # HID
				if iface.bInterfaceSubClass == 1: # Boot
					if iface.bInterfaceProtocol == 1: # Keyboard
						return True
	return False

class Keyboard():
	def __init__(self, device):
		self.device = device
		for config in device:
			for iface in config:
				if iface.bInterfaceClass == 3: # HID
					if iface.bInterfaceSubClass == 1: # Boot
						if iface.bInterfaceProtocol == 1: # Keyboard
							self.config = config
							self.iface = iface
							return
		raise ValueError('Not a boot keyboard')

	def id_string(self):
		return '%04X:%04X' % (self.device.idVendor, self.device.idProduct)

	def vendor_string(self):
		try:
			return self.device.manufacturer
		except Exception:
			return '<Unknown Vendor>'

	def product_string(self):
		try:
			return self.device.product
		except Exception:
			return '<Unknown Product>'

	def print_info(self, prefix=''):
		print('%s%s %s %s' % (prefix, self.id_string(), self.vendor_string(), self.product_string()))

	def claim(self):
		self._is_kda = [self.device.is_kernel_driver_active(i) for i in range(self.config.bNumInterfaces)]
		[self.device.detach_kernel_driver(i) for i in range(self.config.bNumInterfaces) if self._is_kda[i]]
		usb.util.claim_interface(self.device, self.iface.bInterfaceNumber)

	def release(self):
		usb.util.release_interface(self.device, self.iface.bInterfaceNumber)
		[self.device.attach_kernel_driver(i) for i in range(self.config.bNumInterfaces) if self._is_kda[i]]

	def read(self, timeout=None):
		return self.iface[0].read(8, timeout)

	def set_leds(self, leds):
		self.device.ctrl_transfer(0x21, 0x09, 0x0200, self.iface.index, bytes([leds]))

# =================================== MAIN =================================== #

font = PIL.ImageFont.load('sixenate.pil')
display = BonnetDisplay(128, 64)
buttons = BonnetButtons()

def menu_display(items, index, noItems='No items.'):
	display.clear()
	y = (display.height - 8) // 2
	if items:
		display.draw.rectangle((0, y, display.width-1, y + 7), outline=1, fill=1)
		display.draw.text((0, y), items[index], fill=0, font=font)
		for i in range(len(items)):
			if i != index:
				y = (display.height - 8) // 2 + (i - index) * 8
				if -8 < y < display.height:
					display.draw.text((0, y), items[i], fill=1, font=font)
	else:
		display.draw.text((0, y), noItems, fill=1, font=font)
	display.show()

# --------------------------- USB Keyboard Monitor --------------------------- #

def keeb_display_input_report_modifiers(mods):
	display.draw.text((0, 0), '%02X' % mods, fill=1, font=font)
	display.draw.text((24, 0), 'L:', fill=1, font=font)
	display.draw.text((80, 0), 'R:', fill=1, font=font)
	if mods & 0x01: # Left Ctrl
		display.draw.text((40, 0), '\x06', fill=1, font=font)
	if mods & 0x02: # Left Shift
		display.draw.text((48, 0), '\x05', fill=1, font=font)
	if mods & 0x04: # Left Alt
		display.draw.text((56, 0), '\x07', fill=1, font=font)
	if mods & 0x08: # Left Meta
		display.draw.text((64, 0), '\x13', fill=1, font=font)
	if mods & 0x10: # Right Ctrl
		display.draw.text((96, 0), '\x06', fill=1, font=font)
	if mods & 0x20: # Right Shift
		display.draw.text((104, 0), '\x05', fill=1, font=font)
	if mods & 0x40: # Right Alt
		display.draw.text((112, 0), '\x07', fill=1, font=font)
	if mods & 0x80: # Right Meta
		display.draw.text((120, 0), '\x13', fill=1, font=font)

def keeb_display_input_report(input_report, old_input_report=None):
	if old_input_report is None:
		display.clear()
	if old_input_report is not None and old_input_report[0] != input_report[0]:
		display.draw.rectangle((0, 0, display.width-1, 7), outline=0, fill=0)
	if old_input_report is None or old_input_report[0] != input_report[0]:
		keeb_display_input_report_modifiers(input_report[0])
	if old_input_report is not None and old_input_report[1] != input_report[1]:
		display.draw.rectangle((0, 8, display.width-1, 15), outline=0, fill=0)
	if old_input_report is None or old_input_report[1] != input_report[1]:
		display.draw.text((0, 8), '%02X' % input_report[1], fill=1, font=font)
	for i in range(2, len(input_report)):
		if old_input_report is not None and old_input_report[i] != input_report[i]:
			display.draw.rectangle((0, i*8, display.width-1, i*8+7), outline=0, fill=0)
		if old_input_report is None or old_input_report[i] != input_report[i]:
			display.draw.text((0, i*8), CODES_USB[input_report[i]], fill=1, font=font)
	display.show()

def keeb_display_leds(leds, index):
	display.clear()
	x = display.width - 24
	for i, m, s in [(0,0x01,'Num Lock'), (1,0x02,'Caps Lock'),
	                (2,0x04,'Scroll Lock'), (3,0x08,'Compose'),
	                (4,0x10,'Kana'), (5,0x20,'0x20'),
	                (6,0x40,'0x40'), (7,0x80,'0x80')]:
		if i == index:
			display.draw.rectangle((0, i*8, display.width-1, i*8+7), outline=1, fill=1)
		s2 = (' On' if (leds & m) else 'Off')
		fill = (0 if (i == index) else 1)
		display.draw.text((0, i*8), s, fill=fill, font=font)
		display.draw.text((x, i*8), s2, fill=fill, font=font)
	display.show()

class KeyboardTask():
	def activate(self):
		pass
	def button_event(self, button):
		pass
	def input_event(self, input_report):
		pass
	def suspend(self):
		pass

class KeyboardLiveTask(KeyboardTask):
	def __init__(self):
		self.active = False
		self.input_report = b'\x00' * 8
	def activate(self):
		self.active = True
		keeb_display_input_report(self.input_report)
	def input_event(self, input_report):
		if self.active:
			keeb_display_input_report(input_report, self.input_report)
		self.input_report = input_report
	def suspend(self):
		self.active = False
		display.clear()
		display.show()

class KeyboardReportLogTask(KeyboardTask):
	def __init__(self):
		self.active = False
		self.input_reports = []
		self.strings = []
		self.index = 0
	def activate(self):
		self.active = True
		menu_display(self.strings, self.index, 'No reports.')
	def button_event(self, button):
		if button == BonnetButtons.UP:
			if self.index > 0:
				self.index -= 1
				menu_display(self.strings, self.index, 'No reports.')
			buttons.wait_for_release()
		if button == BonnetButtons.DOWN:
			if self.index < len(self.strings)-1:
				self.index += 1
				menu_display(self.strings, self.index, 'No reports.')
			buttons.wait_for_release()
		if button == BonnetButtons.A:
			if self.input_reports:
				self.active = False
				keeb_display_input_report(self.input_reports[self.index])
				time.sleep(0.1)
				button = buttons.read()
				while button:
					if button & BonnetButtons.B:
						self.input_reports = []
						self.strings = []
						self.index = 0
						menu_display(self.strings, self.index, 'No reports.')
						buttons.wait_for_release()
						self.active = True
						return
					time.sleep(0.1)
					button = buttons.read()
				menu_display(self.strings, self.index, 'No reports.')
				self.active = True
			else:
				buttons.wait_for_release()
	def input_event(self, input_report):
		follow = (self.index >= len(self.strings)-1)
		self.input_reports.append(input_report)
		self.strings.append(''.join('%02X' % b for b in input_report))
		if follow:
			self.index = len(self.strings)-1
		if self.active:
			menu_display(self.strings, self.index, 'No reports.')
	def suspend(self):
		self.active = False
		display.clear()
		display.show()

class KeyboardEventLogTask(KeyboardTask):
	def __init__(self):
		self.active = False
		self.input_report = b'\x00' * 8
		self.strings = []
		self.index = 0
	def activate(self):
		self.active = True
		menu_display(self.strings, self.index, 'No events.')
	def button_event(self, button):
		if button == BonnetButtons.UP:
			if self.index > 0:
				self.index -= 1
				menu_display(self.strings, self.index, 'No events.')
			buttons.wait_for_release()
		if button == BonnetButtons.DOWN:
			if self.index < len(self.strings)-1:
				self.index += 1
				menu_display(self.strings, self.index, 'No events.')
			buttons.wait_for_release()
		if button == BonnetButtons.A:
			time.sleep(0.1)
			button = buttons.read()
			while button:
				if button & BonnetButtons.B:
					self.strings = []
					self.index = 0
					menu_display(self.strings, self.index, 'No events.')
					buttons.wait_for_release()
					return
				time.sleep(0.1)
				button = buttons.read()
	def input_event(self, input_report):
		follow = (self.index >= len(self.strings)-1)
		mods_pressed = input_report[0] &~ self.input_report[0]
		mods_released = self.input_report[0] &~ input_report[0]
		keys_pressed = [k for k in input_report[2:] if k and k not in self.input_report[2:]]
		keys_released = [k for k in self.input_report[2:] if k and k not in input_report[2:]]
		for m, k in [(0x01,0xE0),(0x02,0xE1),(0x04,0xE2),(0x08,0xE3),(0x10,0xE4),(0x20,0xE5),(0x40,0xE6),(0x80,0xE7)]:
			if mods_released & m:
				self.strings.append(CODES_USB[k][:2] + '\x19' + CODES_USB[k][3:])
		for k in keys_released:
			self.strings.append(CODES_USB[k][:2] + '\x19' + CODES_USB[k][3:])
		for m, k in [(0x01,0xE0),(0x02,0xE1),(0x04,0xE2),(0x08,0xE3),(0x10,0xE4),(0x20,0xE5),(0x40,0xE6),(0x80,0xE7)]:
			if mods_pressed & m:
				self.strings.append(CODES_USB[k][:2] + '\x10' + CODES_USB[k][3:])
		for k in keys_pressed:
			self.strings.append(CODES_USB[k][:2] + '\x10' + CODES_USB[k][3:])
		if follow:
			self.index = len(self.strings)-1
		if self.active:
			menu_display(self.strings, self.index, 'No events.')
		self.input_report = input_report
	def suspend(self):
		self.active = False
		display.clear()
		display.show()

class KeyboardLEDTask(KeyboardTask):
	def __init__(self, keyboard):
		self.keyboard = keyboard
		self.leds = 0
		self.index = 0
	def activate(self):
		keeb_display_leds(self.leds, self.index)
	def button_event(self, button):
		if button == BonnetButtons.UP:
			if self.index > 0:
				self.index -= 1
				keeb_display_leds(self.leds, self.index)
			buttons.wait_for_release()
		if button == BonnetButtons.DOWN:
			if self.index < 7:
				self.index += 1
				keeb_display_leds(self.leds, self.index)
			buttons.wait_for_release()
		if button == BonnetButtons.A:
			leds = self.leds ^ (1 << self.index)
			try:
				self.keyboard.set_leds(leds)
				self.leds = leds
				keeb_display_leds(self.leds, self.index)
			except Exception:
				traceback.print_exc()
			buttons.wait_for_release()
	def suspend(self):
		display.clear()
		display.show()

class KeyboardMainTask(KeyboardTask):
	def __init__(self, keyboard):
		self.lock = threading.Lock()
		self.active = False
		self.subtasks = [KeyboardLiveTask(), KeyboardReportLogTask(), KeyboardEventLogTask(), KeyboardLEDTask(keyboard)]
		self.index = 0
	def activate(self):
		with self.lock:
			self.active = True
			self.subtasks[self.index].activate()
	def button_event(self, button):
		with self.lock:
			if button == BonnetButtons.LEFT:
				self.subtasks[self.index].suspend()
				self.index -= 1
				if self.index < 0:
					self.index += len(self.subtasks)
				self.subtasks[self.index].activate()
				buttons.wait_for_release()
			elif button == BonnetButtons.RIGHT:
				self.subtasks[self.index].suspend()
				self.index += 1
				if self.index >= len(self.subtasks):
					self.index -= len(self.subtasks)
				self.subtasks[self.index].activate()
				buttons.wait_for_release()
			elif button:
				self.subtasks[self.index].button_event(button)
	def input_event(self, input_report):
		with self.lock:
			for subtask in self.subtasks:
				subtask.input_event(input_report)
	def suspend(self):
		with self.lock:
			self.active = False
			self.subtasks[self.index].suspend()

def keeb_thread(k, task, stopper):
	try:
		k.claim()
		task.activate()
		while not stopper.is_set():
			try:
				input_report = k.read(100)
				task.input_event(input_report)
			except usb.core.USBTimeoutError:
				continue
		task.suspend()
		k.release()
	except Exception:
		traceback.print_exc()

def keeb_run(k):
	task = KeyboardMainTask(k)
	stopper = threading.Event()
	thread = threading.Thread(target=keeb_thread, args=(k, task, stopper))
	thread.start()
	while thread.is_alive():
		b = buttons.read()
		if b == BonnetButtons.B:
			buttons.wait_for_release()
			stopper.set()
			thread.join()
			break
		elif b:
			task.button_event(b)
	display.clear()
	display.show()

# ---------------------------- USB Keyboard Menu ----------------------------- #

def keeblist_display_keeb(y, k, fill=1):
	display.draw.text((0, y), k.id_string(), fill=fill, font=font)
	display.draw.text((0, y+8), k.vendor_string(), fill=fill, font=font)
	display.draw.text((0, y+16), k.product_string(), fill=fill, font=font)

def keeblist_display(keyboards, index):
	display.clear()
	if keyboards:
		y = (display.height - 24) // 2
		display.draw.rectangle((0, y, display.width-1, y + 23), outline=1, fill=1)
		keeblist_display_keeb(y, keyboards[index], fill=0)
		for i in range(len(keyboards)):
			if i != index:
				y = (display.height - 24) // 2 + (i - index) * 32
				if -24 < y < display.height:
					keeblist_display_keeb(y, keyboards[i])
	else:
		y = (display.height - 8) // 2
		display.draw.text((0, y), 'No keyboards.', fill=1, font=font)
	display.show()

def keeblist_reindex(keyboards, sel_id, index):
	for i in range(len(keyboards)):
		if keyboards[i].id_string() == sel_id:
			return i
	return max(0, min(index, len(keyboards)-1))

def keeblist_run():
	devices = usb.core.find(find_all=True, custom_match=isBootKeyboard)
	keyboards = [Keyboard(device) for device in devices]
	index = 0
	keeblist_display(keyboards, index)
	while True:
		b = buttons.read()
		if b == BonnetButtons.A:
			buttons.wait_for_release()
			if keyboards:
				keeb_run(keyboards[index])
			sel_id = keyboards[index].id_string() if keyboards else None
			devices = usb.core.find(find_all=True, custom_match=isBootKeyboard)
			keyboards = [Keyboard(device) for device in devices]
			index = keeblist_reindex(keyboards, sel_id, index)
			keeblist_display(keyboards, index)
		if b == BonnetButtons.B:
			buttons.wait_for_release()
			break
		if b == BonnetButtons.UP:
			if index > 0:
				index -= 1
				keeblist_display(keyboards, index)
			buttons.wait_for_release()
		if b == BonnetButtons.DOWN:
			if index < len(keyboards)-1:
				index += 1
				keeblist_display(keyboards, index)
			buttons.wait_for_release()
		if b == BonnetButtons.LEFT or b == BonnetButtons.RIGHT:
			sel_id = keyboards[index].id_string() if keyboards else None
			devices = usb.core.find(find_all=True, custom_match=isBootKeyboard)
			keyboards = [Keyboard(device) for device in devices]
			index = keeblist_reindex(keyboards, sel_id, index)
			keeblist_display(keyboards, index)
			buttons.wait_for_release()
	display.clear()
	display.show()

# -------------------------------- Main Menu --------------------------------- #

keeblist_run()
