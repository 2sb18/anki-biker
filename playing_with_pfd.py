import pifacedigitalio

def print_hello(event):
  print(event.pin_num)

pifacedigital = pifacedigitalio.PiFaceDigital()
listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
listener.register(0,pifacedigitalio.IODIR_FALLING_EDGE, print_hello)
listener.activate()

