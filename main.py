# main.py
import voltageSensor
import temperatureSensor
import rfDiodeSensor
import cli

vsensor=voltageSensor.voltageSensor()
tsensor=temperatureSensor.temperatureSensor()
rfds = rfDiodeSensor.rfDiodeSensor(vsensor, tsensor)

cli = cli.CLI(rfds)
cli.run()

