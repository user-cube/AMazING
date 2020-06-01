from flask import Flask, request, json, jsonify
from flask_api import status
from flask_restful import Api, Resource, reqparse
import subprocess
import os
import netifaces as ni
import socket
import iwlist

app = Flask(__name__)
api = Api(app)
flagAP=0

@app.route("/")
def hello():
	return "root API amazing PEI \n"
	
@app.route('/<interface>/up')
def apu_interface_up(interface):
	print(interface)
	try:
		com = "sudo ifconfig " + interface + " up "
		#out = subprocess.check_output("sudo ifconfig wlp1s0 up ", shell=True)
		print(com)
		out = subprocess.check_output(com, shell=True)
	except Exception as e:
		content = {'msg': 'Error turning interface up!'}
		return content, status.HTTP_400_BAD_REQUEST
	msg = 'Interface ' + interface + ' UP!'
	return jsonify({'msg':  msg})

@app.route('/<interface>/down')
def apu_interface_down(interface):
	try:
		com = "sudo service dnsmasq stop "
		out = subprocess.check_output(com, shell=True)

		com = "sudo ip addr flush dev " + interface
		out = subprocess.check_output(com, shell=True)

		com = "sudo ifconfig " + interface + " down "
		out = subprocess.check_output(com, shell=True)

		try:
			out = subprocess.check_output("sudo killall wpa_supplicant", shell=True)
			out = out + subprocess.check_output("sudo killall dhclient", shell=True)
		except Exception as e:
			print(e)

		try:
			com = "sudo killall hostapd "
			out = subprocess.check_output(com, shell=True)
			flagAP = 0
		except Exception as e:
			print(e)


	except Exception as e:
		content = {'msg': 'Error turning interface down!'}
		return content, status.HTTP_400_BAD_REQUEST
	msg = 'Interface ' + interface + ' Down!'
	return jsonify({'msg':  msg})


@app.route('/<intf>/scan')
def apu_interface_scan(intf):
	try:
		#raw_data = request.get_json(force=True)
		content = iwlist.scan(interface=intf)
		cells = iwlist.parse(content)
		#print({'msg': cells})
		return {'msg': cells}
	except Exception as e:
		content = {'msg': 'Error Scanning!'}
		return content, status.HTTP_400_BAD_REQUEST


@app.route("/newAP", methods=['POST'])
def createAP():
	raw_data = request.get_json(force=True)
	print(raw_data)
	try:
		global flagAP
		if(flagAP==1):
			content = {'msg': 'AccessPoint already active!'}
			return content, status.HTTP_400_BAD_REQUEST
		args=request.get_json()
		print(args)
		interf = args.get('interface')
		APSSID = args.get('APSSID')
		APPW = args.get('APPW')
		Channel = args.get('Channel')
		RangeStart = args.get('RangeStart')
		RangeEnd = args.get('RangeEnd')
		hw_mode = args.get('hw_mode')
		DFGateway = args.get('DFGateway')
		Netmask = args.get('Netmask')

		out = subprocess.check_output("sudo ifconfig " + interf + " up", shell=True)

		# AP WITH NO PW
		if APPW == "":
			print('SEM PASS')
			out = subprocess.check_output('printf "interface='+interf+'\ndriver=nl80211\nssid=' + APSSID + '\nhw_mode=' + hw_mode + '\nchannel='+ Channel + '\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0"  > /etc/hostapd/hostapd.conf', shell=True)
			out = subprocess.check_output('printf "interface='+interf+'\ndhcp-range=' + RangeStart + ',' + RangeEnd + ',' + Netmask + ',12h\ndhcp-option=3\ndhcp-option=6" > /etc/dnsmasq.conf', shell=True)
			out = subprocess.check_output('sysctl -w net.ipv4.ip_forward=1', shell=True)
			out = subprocess.check_output("sudo ifconfig " + interf + " " + DFGateway + " netmask " + Netmask, shell=True)
			out = subprocess.check_output("sudo hostapd -B /etc/hostapd/hostapd.conf", shell=True)
			out = subprocess.check_output("sudo /etc/init.d/dnsmasq restart", shell=True)
		# AP WITH PASSWORD
		else:
			print('COM PASS')
			out = subprocess.check_output('printf "interface='+interf+'\ndriver=nl80211\nssid=' + APSSID + '\nhw_mode=' + hw_mode + '\nchannel='+ Channel + '\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=3\nwpa_passphrase=' + APPW + '\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"  > /etc/hostapd/hostapd.conf', shell=True)
			out = subprocess.check_output('printf "interface='+interf+'\ndhcp-range=' + RangeStart + ',' + RangeEnd + ',' + Netmask + ',12h\ndhcp-option=3\ndhcp-option=6" > /etc/dnsmasq.conf', shell=True)
			out = subprocess.check_output('sysctl -w net.ipv4.ip_forward=1', shell=True)
			out = subprocess.check_output("sudo ifconfig " + interf + " " + DFGateway + " netmask " + Netmask, shell=True)
			out = subprocess.check_output("sudo hostapd -B /etc/hostapd/hostapd.conf", shell=True)
			out = subprocess.check_output("sudo /etc/init.d/dnsmasq restart", shell=True)
		flagAP=1
		out = json.dumps({'msg': 'AccessPoint Created!'})
		return out
	except subprocess.CalledProcessError as e:
		out = subprocess.check_output("sudo service dnsmasq stop", shell=True)
		out = subprocess.check_output("sudo killall hostapd", shell=True)
		out = subprocess.check_output("sudo ip addr flush dev" + interf, shell=True)
			
		return json.dumps(e.output.decode("utf-8"))




@app.route("/testi")
def getIps():
	hn = socket.gethostname()
	main = {'hostname': hn}
	dic = {}
	li = ni.interfaces()
	for i in li:
		try:
			# print(i)
			addrs = ni.ifaddresses(i)
			# print(addrs)
			addrs = addrs[ni.AF_INET]
			# print(addrs)
			ip = ni.ifaddresses(i)[ni.AF_INET][0]['addr']
			mac = ni.ifaddresses(i)[ni.AF_LINK][0]['addr']
			dic[i] = {'ip': ip, 'mac': mac, 'addrs': addrs, 'logic_state': "UP"}
		except:
			# print(check_interface(i))
			# ip = ni.ifaddresses(i)[ni.AF_INET][0]['addr']
			stri = os.popen("ip a | grep " + i).read()
			if("UP" in stri):
				mac = ni.ifaddresses(i)[ni.AF_LINK][0]['addr']
				dic[i] = {'ip': None, 'mac': mac, 'addrs': None, 'logic_state': "UP"}
			else:
				mac = ni.ifaddresses(i)[ni.AF_LINK][0]['addr']
				dic[i] = {'ip': None, 'mac': mac, 'addrs': None, 'logic_state': "DOWN"}
	main['interfaces']=dic
	return jsonify(main)


@app.route("/teste")
def getTest():
	os.system("netstat -i | awk '{print $1}'>interface.txt")
	with open("interface.txt", "r") as f:
		text = f.read()

	text = text.split("\n")
	del text[0]
	del text[len(text)-1]
	return jsonify(text)

@app.route("/<interf>/connect", methods=['POST'])
def connect(interf):
	raw_data = request.get_json(force=True)
	print(raw_data)

	ssid = raw_data.get('SSID')
	pw = raw_data.get('PASS')


	try:
		if pw != "":
			print("Ligar com Pass!")
			command = "wpa_passphrase " + ssid + " " + pw + " | sudo tee /etc/wpa_supplicant.conf"
			out = subprocess.check_output(command, shell=True)
			command2 = "sudo wpa_supplicant -B -c /etc/wpa_supplicant.conf -i " + interf
			out = out + subprocess.check_output(command2, shell=True)
			command3 = "sudo dhclient -v " + interf
			out = out + subprocess.check_output(command3, shell=True)
		else:
			print("Ligar Sem Pass!")

			command1 = "sudo iwconfig " + interf + " essid " + ssid
			print(command1)
			out = subprocess.check_output(command1, shell=True)
			print(out)

			command3 = "sudo dhclient -v " + interf
			print(command3)
			out = subprocess.check_output(command3, shell=True)
			print(out)
		
		content = {'msg': 'Connected to' + ssid + '!'}
		return content

	except Exception as e:
		content = {'msg': 'Error Connecting to ' + ssid + '!'}
		print(e)
		return content, status.HTTP_400_BAD_REQUEST



class connection(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			global flagAP
			args=request.get_json()		
			if(len(args) == 3):
				SSID = args.get('SSID')
				PASS = args.get('PASS')
				NetwC = args.get('NetwC')
				if(flagAP==1 and NetwC=="wlp5s0"):
					out = json.dumps({'Message': 'wlp5s0 is being used as an access point'})
					return out
				command = "wpa_passphrase " + SSID + " " + PASS + " | sudo tee /etc/wpa_supplicant.conf"
				out = subprocess.check_output(command, shell=True)
				command2 = "sudo wpa_supplicant -B -c /etc/wpa_supplicant.conf -i " + NetwC
				out = out + subprocess.check_output(command2, shell=True)
				command3 = "sudo dhclient -v " + NetwC
				out = out + subprocess.check_output(command3, shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect arg number, needs to be 3'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e)

class disconnect(Resource):
	def get(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)		
			out = subprocess.check_output("sudo killall wpa_supplicant", shell=True)
			out = out + subprocess.check_output("sudo killall dhclient", shell=True)
			out = out.decode("utf-8") 
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class postGetApIP(Resource):
	def get(self):
		if(flagAP==1):
			try:
				out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
				out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)		
				out = subprocess.check_output("cat /var/lib/misc/dnsmasq.leases", shell=True)
				out = out.decode("utf-8") 
				return out
			except subprocess.CalledProcessError as e:
				return json.dumps(e.output.decode("utf-8"))
		else:
			out = json.dumps({'Message': 'There is no AccessPoint activated'})

class changeIP(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args=request.get_json()
			IP = args.get('IP')
			NetwC = args.get('NetwC')
			Netmask = args.get('Netmask')
			if(len(args) == 3):
				command = "sudo ifconfig " + NetwC + " " + IP + " netmask " + Netmask
				out = subprocess.check_output(command, shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect arg number, needs to be 2'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class getifconfig(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			if(len(args) == 1):
				out = subprocess.check_output("sudo ifconfig | grep -m1 '" + NetwC + "' -A 1", shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect arg number, needs to be 1'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))	

class getlist(Resource):
	def get(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			out = subprocess.check_output("iw list", shell=True)
			out = out.decode("utf-8")
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class CreateAccessPoint(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			global flagAP
			if(flagAP==1):
				out = json.dumps({'Message': 'AccessPoint already active'})
				out = out.decode("utf-8")
				return out
			args=request.get_json()
			APSSID = args.get('APSSID')
			APPW = args.get('APPW')
			Channel = args.get('Channel')
			RangeStart = args.get('RangeStart')
			RangeEnd = args.get('RangeEnd')
			hw_mode = args.get('hw_mode')
			DFGateway = args.get('DFGateway')
			Netmask = args.get('Netmask')
			out = subprocess.check_output('printf "interface=wlp5s0\ndriver=nl80211\nssid=' + APSSID + '\nhw_mode=' + hw_mode + '\nchannel='+ Channel + '\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=3\nwpa_passphrase=' + APPW + '\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"  > /etc/hostapd/hostapd.conf', shell=True)
			out = subprocess.check_output('printf "interface=wlp5s0\ndhcp-range=' + RangeStart + ',' + RangeEnd + ',' + Netmask + ',12h\ndhcp-option=3\ndhcp-option=6" > /etc/dnsmasq.conf', shell=True)
			out = subprocess.check_output('sysctl -w net.ipv4.ip_forward=1', shell=True)
			out = subprocess.check_output("sudo ifconfig wlp5s0 " + DFGateway + " netmask " + Netmask, shell=True)
			out = subprocess.check_output("sudo hostapd -B /etc/hostapd/hostapd.conf", shell=True)		
			out = subprocess.check_output("sudo /etc/init.d/dnsmasq restart", shell=True)
			out = out.decode("utf-8")
			flagAP=1
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class StopAccessPoint(Resource):
	def get(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			global flagAP
			if(flagAP == 1):
				out = subprocess.check_output("sudo service dnsmasq stop", shell=True)
				out = subprocess.check_output("sudo killall hostapd", shell=True)
				out = out.decode("utf-8")
				flagAP=0
				return out
			else:
				out = json.dumps({'Message':'There is no AccessPoint to stop.'})
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))		


class scan(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			if(len(args) == 1):
				out = subprocess.check_output("sudo iw dev " + NetwC + " scan", shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class localwireless(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			if(len(args) == 1):
				out = subprocess.check_output("sudo ifconfig " + NetwC + " up", shell=True)
				out = subprocess.check_output("sudo iw " + NetwC + " scan | grep 'SSID\|freq\|signal'", shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))
	
class link(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			if(len(args) == 1):
				out = subprocess.check_output("iw dev " + NetwC + " link", shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class stationstats(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			if(len(args) == 1):
				out = subprocess.check_output("iw dev " + NetwC + " station dump", shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))


class stationpeerstats(Resource):
	def get(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args=request.get_json()
			NetwC = args.get('NetwC')
			MAC = args.get('MAC')
			if(len(args) == 2):
				out = subprocess.check_output("sudo iw dev " + NetwC + " station get " + MAC, shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))
		
class modtxhtmcsbitrates(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			Lbits = args.get('Lbits')
			if(len(args) == 1):
				out = subprocess.check_output("iw " + NetwC + " set bitrates " + Lbits, shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard and the bits'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

class settingtxpowerdev(Resource):
	def post(self):
		try:
			out = subprocess.check_output("ifconfig wlp1s0 up ", shell=True)
			out = subprocess.check_output("ifconfig wlp5s0 up ", shell=True)
			args = request.get_json()
			NetwC = args.get('NetwC')
			Type = args.get('Type')
			Power = args.get('Power')
			if(len(args) == 1):
				out = subprocess.check_output("iw dev " + NetwC + " " + Type + " " + Power, shell=True)
				out = out.decode("utf-8")
			else:
				out = json.dumps({'Message': 'Incorrect args, needs to receive the NetworkCard'})
			return out
		except subprocess.CalledProcessError as e:
			return json.dumps(e.output.decode("utf-8"))

api.add_resource(connection, '/connection')					#POST e GET
api.add_resource(disconnect, '/disconnect')					#GET
api.add_resource(postGetApIP, '/postGetApIP')				#GET
api.add_resource(changeIP, '/changeIP')						#POST e GET
api.add_resource(getifconfig,'/getifconfig')				#POST
api.add_resource(getlist, '/getlist')						#GET
api.add_resource(CreateAccessPoint, '/CreateAccessPoint')	#POST
api.add_resource(StopAccessPoint, '/StopAccessPoint')		#GET
api.add_resource(scan,'/scan')								#POST
api.add_resource(localwireless,'/localwireless')			#POST
api.add_resource(link,'/link')								#POST
api.add_resource(stationstats,'/stationstats')				#POST
api.add_resource(stationpeerstats, '/stationpeerstats')		#POST
api.add_resource(modtxhtmcsbitrates,'/modtxhtmcsbitrates')	#POST
api.add_resource(settingtxpowerdev,'/settingtxpowerdev')	#POST

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
