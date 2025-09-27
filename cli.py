# Simple MicroPython CLI with command history, rate-limited output, interrupt/pause/resume, and parse-friendly output
import sys
import time
import rfDiodeSensor

try:
	import uos as os
except ImportError:
	import os

HISTORY_SIZE = 10
RATE_LIMIT_MS = 200  # milliseconds between outputs

class CLI:
	def __init__(self, rfDiodeSensor):
		self.rfDiodeSensor = rfDiodeSensor
		self.commands = {
			'?': self.cmd_help,
			'v': self.cmd_readV,
			't': self.cmd_readT,
			'p': self.cmd_readP,
			'a': self.cmd_readAll,
			'l': self.cmd_loop,
			'x': self.cmd_exit,
		}
		self.running = True
		self.history = []
		self.history_index = None
		self.paused = False

	def run(self):
		print('RF Power Sensor CLI. Type ? for commands.')
		while self.running:
			try:
				line = self.input_with_history('> ')
				if not line:
					continue
				self.add_history(line)
				cmd, *args = line.strip().split()
				if cmd in self.commands:
					self.commands[cmd](args)
				else:
					print('ERR: Unknown command')
			except KeyboardInterrupt:
				print('\nInterrupted')
			except Exception as e:
				print('ERR:', e)

	def input_with_history(self, prompt):
		# Basic input with history navigation using up/down arrows
		# MicroPython REPL does not support arrow keys natively, so this is a stub for real hardware integration
		# For actual hardware, use UART and implement key handling
		return input(prompt)

	def add_history(self, line):
		if line and (not self.history or self.history[-1] != line):
			self.history.append(line)
			if len(self.history) > HISTORY_SIZE:
				self.history.pop(0)

	def cmd_help(self, args):
		print('OK: Commands: ? (help),       v (read voltage), t (read temperature),')
		print('              p (read power), a (read all),     l <count> (loop),')
		print('              x (exit)')

	def cmd_readV(self, args):
		voltage = self.rfDiodeSensor.readVoltage()
		print('voltage: ', voltage)	
	
	def cmd_readT(self, args):
		temperature = self.rfDiodeSensor.readTemperature()
		print('temperature: ', temperature)
	
	def cmd_readP(self, args):
		power = self.rfDiodeSensor.readPower()
		print('power: ', power)
	
	def cmd_readAll(self, args):
		voltage = self.rfDiodeSensor.readVoltage()
		temperature = self.rfDiodeSensor.readTemperature()
		power = self.rfDiodeSensor.readPower()
		print('voltage: %f temperature: %.2f power: %f' % (voltage, temperature, power))

	def cmd_echo(self, args):
		print('OK:', ' '.join(args))

	def cmd_loop(self, args):
		count = int(args[0]) if args else 10
		print('OK: Starting loop, Ctrl-C to interrupt')
		i = 0
		try:
			while i < count:
				if self.paused:
					time.sleep(0.1)
					continue
				print('index: %d ' % i, end="")
				self.cmd_readAll([])
				i += 1
				self.handle_pause()
				time.sleep(RATE_LIMIT_MS / 1000)
		except KeyboardInterrupt:
			print('OK: Loop interrupted')

	def handle_pause(self):
		# Stub: In real hardware, check for space bar press to pause/resume
		# On MicroPython REPL, this is not natively supported
		pass

	def cmd_exit(self, args):
		print('OK: Exiting CLI')
		self.running = False

if __name__ == '__main__':
    import voltageSensor
    import temperatureSensor    
    
    vsensor=voltageSensor.voltageSensor()
    tsensor=temperatureSensor.temperatureSensor()
    rfds = rfDiodeSensor.rfDiodeSensor(vsensor, tsensor)

    cli = CLI(rfds)
    cli.run()

