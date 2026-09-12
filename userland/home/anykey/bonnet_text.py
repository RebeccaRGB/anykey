import adafruit_ssd1306
import board
import busio
import digitalio
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

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

font = PIL.ImageFont.load('sixenate.pil')
display = BonnetDisplay(128, 64)
display.draw.text((0, 0), 'Hello, World!', fill=1, font=font)
display.show()

button_string = 'ablrudc'
buttons = BonnetButtons()

while True:
	try:
		b = buttons.read()
		bs = ''.join(button_string[i].upper() if (b & (1 << i)) else button_string[i].lower() for i in range(len(button_string)))
		display.draw.rectangle((0, 16, 56, 24), outline=0, fill=0)
		display.draw.text((0, 16), bs, fill=1, font=font)
		display.show()
	except KeyboardInterrupt:
		break

display.clear()
display.show()
