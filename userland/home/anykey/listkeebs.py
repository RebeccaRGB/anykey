import usb.core

def isBootKeyboard(device):
	for config in device:
		for iface in config:
			if iface.bInterfaceClass == 3: # HID
				if iface.bInterfaceSubClass == 1: # Boot
					if iface.bInterfaceProtocol == 1: # Keyboard
						return True
	return False

for device in usb.core.find(find_all=True, custom_match=isBootKeyboard):
	vid = device.idVendor
	pid = device.idProduct
	ms = device.manufacturer
	ps = device.product
	print('%04X:%04X %s %s' % (vid, pid, ms, ps))
