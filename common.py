import logger
import mysql.connector
import os
import subprocess
import time
import yaml

# with open(os.path.join(os.path.dirname(__file__), 'settings.yml'), 'r') as f:
with open("./settings.yml", 'r') as f:
	settings = yaml.load(f)


def mysql_connect_or_die(database, user, password, host="localhost", port=3306, ssh=None):
	connect_port=port
	connect_host=host
	if ssh is not None:
		connect_host='127.0.0.1'
		connect_port=ssh['port']
		os.system("ssh -L {}:127.0.0.1:{} {}@{} &".format(ssh['port'], port, ssh['user'], ssh['host']))
		print("Sleeping")
		time.sleep(10)
		print("Waking up")

	return mysql.connector.connect(host=connect_host, port=connect_port, database=database, user=user, password=password)

def read_data(fname):
	input_data=None
	with open(fname, 'r') as f:
		input_data = yaml.load(f)
	return input_data

def print_header(first_name, last_name, email, sciper):
	print("\n\n\n")
	print("==================================================================")
	print("first name: {}".format(first_name))
	print("last name:  {}".format(last_name))
	print("email:      {}".format(email))
	print("sciper:     {}".format(sciper))
	print("==================================================================")
