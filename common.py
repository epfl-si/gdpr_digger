import csv
import logger
import mysql.connector
import os
import subprocess
import time
import yaml

# with open(os.path.join(os.path.dirname(__file__), 'settings.yml'), 'r') as f:
with open("./settings.yml", 'r') as f:
	settings = yaml.load(f, Loader=yaml.FullLoader)

# return the minimal set of keys for an heterogeneous list of dictionaries
def common_keys(data):
	keys=[]
	for d in data:
		for k, v in d.items():
			if v is not None and v != '':
				keys.append(k)
	keys = list(dict.fromkeys(keys))
	return keys

def write_csv(path, data, keys=None):
	if keys is None:
		keys=common_keys(data)
	with open(path, 'a', encoding='utf-8') as csvfile:
		w = csv.DictWriter(csvfile, fieldnames=keys, extrasaction='ignore', restval="")
		w.writeheader()
		w.writerows(data)



def mysql_connect_or_die(database, user, password, host="localhost", port=3306, ssh=None):
	connect_port=port
	connect_host=host
	if ssh is not None:
		connect_host='127.0.0.1'
		connect_port=ssh['port']
		cmd = "ssh -L {}:127.0.0.1:{} {}@{} &".format(ssh['port'], port, ssh['user'], ssh['host'])
		print(cmd)
		os.system(cmd)
		print("Sleeping")
		time.sleep(10)
		print("Waking up")

	return mysql.connector.connect(host=connect_host, port=connect_port, database=database, user=user, password=password)

def read_data(fname):
	input_data=None
	with open(fname, 'r') as f:
		input_data = yaml.load(f, Loader=yaml.FullLoader)
	return input_data

def print_header(first_name, last_name, email, sciper):
	print("\n\n\n")
	print("==================================================================")
	print("first name: {}".format(first_name))
	print("last name:  {}".format(last_name))
	print("email:      {}".format(email))
	print("sciper:     {}".format(sciper))
	print("==================================================================")
