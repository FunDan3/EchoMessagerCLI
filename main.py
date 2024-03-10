#! /usr/bin/python3
import aioconsole
import EchoAPI #EchoMessagerAPI
import term

def options_input(text, options):
	while True:
		user_input = input(text)
		if user_input.lower() not in options:
			print(f"Please choose on of these options: {options}")
		else:
			return user_input.lower()

server_addr = input("Server address: ")
if not server_addr.startswith("http"):
	server_addr = "https://" + server_addr
if server_addr.endswith("/"):
	server_addr = server_addr[:len(server_addr)-1]
if server_addr.count(":") == 1:
	server_addr = server_addr + ":23515"

print(f"Connecting to {server_addr}")
client = EchoAPI.Client(server_addr)

@client.event.on_connected
async def connected():
	print(term.textCenter("Terms And Conditions"))
	print(client.server_terms_and_conditions)
	print(term.textCenter("Privacy Policy"))
	print(client.server_privacy_policy)
	print(term.textCenter("By using this server you accept it's Terms And Conditions and Privacy Policy")+"\n"*4)
	action = options_input("Login or Register: ", ["login", "register"])
	register_password_addition = " AND CAN NOT BE RECOVERED IF ENTERED INCORRECTLY" if action == "register" else ""
	action = client.login if action == "login" else client.register


	while True:
		login = input("Login: ")
		password = input(f"Password (IT WILL NOT BE HIDDEN{register_password_addition}): ")
		try:
			await action(login, password)
		except Exception as e:
			print(e)

client.start()
