#! /usr/bin/python3
import aioconsole
import EchoAPI #EchoMessagerAPI
import term
import json
import os

license = f"""EchoMessagerCLI - Messager using peer to peer post-quantum encryption
Copyright (C) 2024 Fun_Dan3

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but {term.blink}{term.bold}{term.red}WITHOUT ANY WARRANTY{term.off}; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
Contact - dfr34560@gmail.com

"""

help_text = """
inbox - Display list of users that messaged you.
read <username> - Read messagess sent from <username>.
exit - Stop the program.
help - Display this message.
"""

for line in license.split("\n"):
	print(term.textCenter(line))

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
messages = {}

@client.event.on_connected
async def on_connected():
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
async def on_login():
	save_settings(settings)
	print("Logged in. Use 'help' to get list of commands")
	while True:
		inp = await aioconsole.ainput(f"{client.username}:{client.user.identity_hash} > ")
		args = inp.split(" ")
		command = args[0]
		args.pop(0)
		if command == "inbox":
			if args:
				print("Command 'inbox' does not take any arguments")
				continue
			for author, new_messages in messages.items():
				author = await client.fetch_user(author)
				print(f"{author.username}:{author.identity_hash} - {len(new_messages)} new messages")
		elif command == "read":
			if len(args)!=1:
				print("Command 'read' takes exactly one argument - 'username'")
				continue
			if args[0] not in messages or not messages[args[0]]:
				print(f"No new messages from '{args[0]}'")
				continue
			author = await client.fetch_user(args[0])
			print(f"Reading messages from {author.username}:{author.identity_hash}...")
			separator = "-" * term.getSize()[1]
			print(separator)
			for message in messages[args[0]]:
				await message.read()
				print(message.content.replace(separator, ""))
				print(separator)
			print(f"{author.username}'s identity hash is {author.identity_hash}. Make sure that it is really their identity before trusting those messages.")
		elif command == "exit":
			if args:
				print("Command 'exit' doesnt take any arguments")
				continue
			exit()
		elif command == "help":
			if args:
				print("Command 'help' doesnt take any arguments")
				continue
			print(help_text)
		else:
			print(f"Unknown command '{command}'")
@client.event.on_message
async def on_message(message):
	if message.author.username not in messages:
		messages[message.author.username] = []
	messages[message.author.username].append(message)
client.start()
