#! /usr/bin/python3
import aioconsole
import EchoAPI #EchoMessagerAPI
import term
import json
import os

def save_settings(settings):
	with open(f"./settings.json", "w") as f:
		f.write(json.dumps(settings))

def read_settings():
	if not os.path.exists("./settings.json"):
		settings = {"AutoConnectIP": "",
			"Credentials": {},
		}
		save_settings(settings)
	else:
		with open("./settings.json", "r") as f:
			settings = json.loads(f.read())
	return settings

def options_input(text, options):
	while True:
		user_input = input(text)
		if user_input.lower() not in options:
			print(f"Please choose on of these options: {options}")
		else:
			return user_input.lower()

settings = read_settings()

if not settings["AutoConnectIP"]:
	server_addr = input("Server address: ")
	if not server_addr.startswith("http"):
		server_addr = "https://" + server_addr
	if server_addr.endswith("/"):
		server_addr = server_addr[:len(server_addr)-1]
	if server_addr.count(":") == 1:
		server_addr = server_addr + ":23515"
	settings["AutoConnectIP"] = server_addr
	save_settings(settings)
else:
	server_addr = settings["AutoConnectIP"]

print(f"Connecting to {server_addr}")
client = EchoAPI.Client(server_addr)

@client.event.on_connected
async def connected():
	if not settings["Credentials"]:
		print(term.textCenter("Terms And Conditions"))
		print(client.server_terms_and_conditions)
		print(term.textCenter("Privacy Policy"))
		print(client.server_privacy_policy)
		print(term.textCenter(f"{term.blink}{term.bold}By using this server you accept it's Terms and Conditions and Privacy Policy{term.off}")+"\n"*4)
		action = options_input("Login or Register: ", ["login", "register"])
		register_password_addition = " AND CAN NOT BE RECOVERED IF ENTERED INCORRECTLY" if action == "register" else ""
		action = client.login if action == "login" else client.register
		while True:
			login = input("Login: ")
			password = input(f"Password ({term.red}{term.bold}IT WILL NOT BE HIDDEN{register_password_addition}{term.off}): ")
			settings["Credentials"]["Login"] = login
			settings["Credentials"]["Password"] = password
			try:
				await action(login, password)
			except Exception as e:
				print(e)
	else:
		await client.login(settings["Credentials"]["Login"], settings["Credentials"]["Password"])

@client.event.on_login
async def logged_in():
	save_settings(settings)

client.start()
