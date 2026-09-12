import threading
import time
import usb.core
import usb.util

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

	def print_info(self, prefix=''):
		vid = self.device.idVendor
		pid = self.device.idProduct
		ms = self.device.manufacturer
		ps = self.device.product
		print('%s%04X:%04X %s %s' % (prefix, vid, pid, ms, ps))

	def claim(self):
		self._is_kda = [self.device.is_kernel_driver_active(i) for i in range(self.config.bNumInterfaces)]
		[self.device.detach_kernel_driver(i) for i in range(self.config.bNumInterfaces) if self._is_kda[i]]
		usb.util.claim_interface(self.device, self.iface.bInterfaceNumber)

	def release(self):
		usb.util.release_interface(self.device, self.iface.bInterfaceNumber)
		[self.device.attach_kernel_driver(i) for i in range(self.config.bNumInterfaces) if self._is_kda[i]]

	def read(self, timeout=None):
		return self.iface[0].read(8, timeout)

devices = usb.core.find(find_all=True, custom_match=isBootKeyboard)
keyboards = [Keyboard(device) for device in devices]

for i in range(len(keyboards)):
	keyboards[i].print_info('%d ' % i)

for k in keyboards:
	k.claim()

def readKeyboard(i, k, stopper):
	while not stopper.is_set():
		try:
			input_report = k.read(100)
			h = ' '.join('%02X' % b for b in input_report)
			print('%d %s' % (i, h))
		except usb.core.USBTimeoutError:
			continue

stoppers = [threading.Event() for k in keyboards]
threads = [threading.Thread(target=readKeyboard, args=(i, keyboards[i], stoppers[i])) for i in range(len(keyboards))]

for t in threads:
	t.start()

while True:
	try:
		time.sleep(1)
	except KeyboardInterrupt:
		break

print('Waiting for threads to stop...')

for s in stoppers:
	s.set()

for t in threads:
	t.join()

for k in keyboards:
	k.release()
