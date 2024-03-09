#! /usr/bin/python3
import aioconsole
import EchoAPI #EchoMessagerAPI

server_addr = input("Server address: ")
if not server_addr.startswith("http"):
	server_addr = "https://" + server_addr
if server_addr.endswith("/"):
	server_addr = server_addr[:len(server_addr)-1]
if server_addr.count(":") == 1:
	server_addr = server_addr + ":23515"

print(f"Connecting to {server_addr}")
client = EchoAPI.Client(server_addr)

client.start()
