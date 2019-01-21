import gc
import machine
import os
import dht
import urequests
import ujson
import network
import time

PIN_DHT = 2
PIN_RELAY = 5
TRIGGER_SLEEP = 0.5

PIN_RELAY_OUT = machine.Pin(PIN_RELAY, machine.Pin.OUT)

def connect_wireless():
	sta_if = network.WLAN(network.STA_IF)
	if not sta_if.isconnected():
		print('connecting to network...')
		sta_if.active(True)
		wirelessauth = read_wireless()
		sta_if.connect(wirelessauth['essid'], wirelessauth['password'])
		while not sta_if.isconnected():
			pass
		print('network config:', sta_if.ifconfig())

def setup_dht():
	d = dht.DHT22(machine.Pin(PIN_DHT))
	return d

def trigger_relay(pin):
	pin.value(1)
	time.sleep(TRIGGER_SLEEP)
	pin.value(0)

def init_config():
	os.mkdir('config')

def save_wireless(essid, password):
	print(os.listdir())
	try:
		os.remove('config/wireless.json')
	except:
		print("config/wireless.json does not exist!")
	f = open('config/wireless.json', 'w')
	settings = {
	"essid": essid,
	"password": password
	}
	f.write(ujson.dumps(settings))

def save_url(url):
        print(os.listdir())
        try:
                os.remove('config/url.json')
        except:
                print("config/url.json does not exist!")
        f = open('config/url.json', 'w')
        settings = {
        "url": url
        }
        f.write(ujson.dumps(settings))


def read_wireless():
	print(os.listdir())
	f = open('config/wireless.json')
	settingsdata = f.read()
	obj = ujson.loads(settingsdata)
	return obj

def read_url():
	print(os.listdir())
	f = open('config/url.json')
	settingsdata = f.read()
	obj = ujson.loads(settingsdata)
	return obj

def run_loop():
	url = read_url()
	linkurl = url['url']
	d = setup_dht()
	timer = 0
	while True:
		gc.collect()
		time.sleep(0.5) # check to open the door every 0.5 secs
		connect_wireless()
		print("Status: Sending data via POST to server!")
		timer = timer + 1
		if timer >= 4:
			d.measure()
			print("temp:", d.temperature())
			print("hum:", d.humidity())
			timer = 0
		# post_data(d)
		data = {
		"temp": d.temperature(),
		"hum": d.humidity()
			}
		headers = {'content-type': 'application/json'}
		jsondata = ujson.dumps(data)
		print(jsondata)
		try:
			response = urequests.post(linkurl, data = jsondata, headers = headers)
			responsejson = ujson.loads(response.text)
			responsejsontoggle = responsejson['toggle']
			if responsejsontoggle:
				trigger_relay(PIN_RELAY_OUT)
				print("Status: toggle switch ", responsejsontoggle, responsejson)
		except:
			print("Error: Could not send POST request or trigger relay")


run_loop()
