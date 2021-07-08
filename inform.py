import glob
import logging
import mysql.connector
import re
import subprocess
import yaml 

from common import *

class InformResult(dict):
	def ciccio():
		return


class InformDigger:
	def __init__(self):
		self.settings = settings['inform']
		self.db=mysql_connect_or_die(**self.settings['db'])	
		self.logfiles=glob.glob("{}*".format(self.settings['httpd_log_path']))

	def search(self, first_name, last_name, email, sciper):

		result = InformResult()

		cursor1 = self.db.cursor(buffered=True)
		cursor2 = self.db.cursor(buffered=True)
		cursor3 = self.db.cursor(dictionary=True, buffered=True)

		# Search on for all the forms that the user might have edited and hence a possible source IP
		forms={}
		if last_name is not None:
			cursor1.execute('SELECT table_name,column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE (column_name LIKE "%name%" or column_name = "nom") AND table_name LIKE "form_%_data" ORDER BY table_name')
			for  (table_name, column_name)  in cursor1:
				# TODO: find a way to also query on columns with invalid names
				if not re.search("[%&-:? ]", column_name):
					forms.setdefault(table_name,{'name': [], 'email': []})
					forms[table_name]['name'].append(column_name)

		if email is not None:
			cursor1.execute('SELECT table_name,column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE column_name LIKE "%mail%" AND table_name LIKE "form_%_data" ORDER BY table_name')
			for  (table_name, column_name)  in cursor1:
				# TODO: find a way to also query on columns with invalid names
				if not re.search("[%&-:? ]", column_name):
					forms.setdefault(table_name,{'name': [], 'email': []})
					forms[table_name]['email'].append(column_name)



		print("\n-------------------------------------------- Infos as InForm user")
		fau = []
		for table_name, cols in forms.items():
			tid = table_name[5:-5]
			sql="SELECT name,label from forms WHERE id={}".format(tid)
			cursor3.execute("SELECT name,label,description from forms WHERE id={}".format(tid))
			table_metadata = cursor3.fetchone()
			table_metadata = {'name': 'No Name', 'label': '--'} if table_metadata is None else table_metadata
			w=[]
			for col in cols['name']:
				w.append("{} = '{}'".format(col, last_name))
			for col in cols['email']:
				w.append("{} = '{}'".format(col, email))

			sql="SELECT * from {} where {}".format(table_name, " OR ".join(w))
			# print(sql)

			try:
				cursor3.execute(sql)
			except: 
				print("Failed to execute the following SQL query: {}".format(sql))
			for row in cursor3:
				d={
					"form_id": tid, 
					"form_name": table_metadata['name'],
					"form_label": table_metadata['label'] 
				}
				dd = {}
				print("\n--------------------- Formulaire {}: {}".format(tid, table_metadata['name']))
				print("--------------------- '{}'".format(table_metadata['label']))
				for k, v in row.items():
					if len(str(v)) > 0:
						dd[k] = v
						print("{}: {}".format(k,v))
				d["form_data"] = dd
				fau.append(d)

		result["Form as User"] = fau
		result["Number of Forms as User"] = len(fau)

		# # Search for a user with given sciper or email
		# if sciper is not None:	
		# 	cursor1.execute("SELECT UserID from users where extID = {}".format(sciper))
		# 	user_id = cursor1.fetchone() if cursor1.with_rows else None
		# elif email is not None:
		# 	cursor1.execute("SELECT UserID from users where email = {}".format(email))
		# 	user_id = cursor1.fetchone() if cursor1.with_rows else None
		user_ids=[]
		cursor3.execute("SELECT UserID from users where extID = {} OR email = '{}'".format(sciper, email))
		if cursor3.with_rows:
			for row in cursor3:
				user_ids.append(row['UserID'])
		print("user_ids={}".format(", ".join(user_ids)))

		# Search for all the forms that the user might have edited and hence a possible source IP
		faa=[]
		if len(user_ids) > 0:
			user_ids = user_ids[0]
			print("\n-------------------------------------------- Infos as InForm administrator")
			print("User ID: {}".format(user_id))
			cursor1.execute("SELECT formid from formroles where userid = {}".format(user_id))
			form_ids = []
			for (formid) in cursor1:
				i=formid[0]
				form_ids.append(i)
				print("The user is administrator for form no. {}".format(i))
			access_ips=[]
			for id in form_ids:
				print(id)
				# Search in the log files for administrative action on the forms and deduce list of IP
				pat="listComponents.php\?formID={}".format(id)
				for f in self.logfilses:
					for line in open(f, 'r'):
						if re.search(pat, line):
							ip=line.split(" ")[0]
							if ip not in access_ips:
								access_ips.append(ip)
			if len(access_ips) > 0:
				print("Possible source addresses: {}".format(", ".join(access_ips)))
			else:
				print("Nothing found in the server logs")


		# # Search for all the forms that the user might have edited and hence a possible source IP
		# faa=[]
		# if user_id is not None:
		# 	user_id = user_id[0]
		# 	print("\n-------------------------------------------- Infos as InForm administrator")
		# 	print("User ID: {}".format(user_id))
		# 	cursor1.execute("SELECT formid from formroles where userid = {}".format(user_id))
		# 	form_ids = []
		# 	for (formid) in cursor1:
		# 		i=formid[0]
		# 		form_ids.append(i)
		# 		print("The user is administrator for form no. {}".format(i))
		# 	access_ips=[]
		# 	for id in form_ids:
		# 		print(id)
		# 		# Search in the log files for administrative action on the forms and deduce list of IP
		# 		pat="listComponents.php\?formID={}".format(id)
		# 		for f in self.logfiles:
		# 			for line in open(f, 'r'):
		# 				if re.search(pat, line):
		# 					ip=line.split(" ")[0]
		# 					if ip not in access_ips:
		# 						access_ips.append(ip)
		# 	if len(access_ips) > 0:
		# 		print("Possible source addresses: {}".format(", ".join(access_ips)))
		# 	else:
		# 		print("Nothing found in the server logs")
		return(result)

if __name__ == '__main__':

	s=InformDigger()
	# s.search(sciper="106366")
	# s.search(sciper="157489")

	# s.search(sciper="236373")

	# s.search(last_name="Mocito", email="cendrine.favez@epfl.ch")

	input_data = read_data("./data.yml")
	for user in input_data:
		print_header(**user)
		r=s.search(**user)
		print(r)