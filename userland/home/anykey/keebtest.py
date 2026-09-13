import threading
import time
import usb.core
import usb.util

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

devices = usb.core.find(find_all=True, custom_match=isBootKeyboard)
keyboards = [Keyboard(device) for device in devices]

for i in range(len(keyboards)):
	keyboards[i].print_info('%d ' % i)

for k in keyboards:
	k.claim()
	k.set_leds(0x07)

def readKeyboard(i, k, stopper):
	while not stopper.is_set():
		try:
			input_report = k.read(100)
			h = ' '.join('%02X' % b for b in input_report)
			print('%d %s' % (i, h))
		except usb.core.USBTimeoutError:
			continue

def writeKeyboard(k, stopper):
	while not stopper.is_set():
		k.set_leds(0x01)
		time.sleep(0.3)
		k.set_leds(0x02)
		time.sleep(0.3)
		k.set_leds(0x04)
		time.sleep(0.3)

stoppers = [threading.Event() for k in keyboards]
threads = [threading.Thread(target=readKeyboard, args=(i, keyboards[i], stoppers[i])) for i in range(len(keyboards))]
wthreads = [threading.Thread(target=writeKeyboard, args=(keyboards[i], stoppers[i])) for i in range(len(keyboards))]

for t in threads:
	t.start()

for t in wthreads:
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

for t in wthreads:
	t.join()

for k in keyboards:
	k.set_leds(0)
	k.release()
