import glob
import gzip
import io
import logging
import mysql.connector
import os
import re
import subprocess
import yaml 

from common import *

class PeopleDB:
	def __init__(self, dbname, dbs_config):
		# Read DB credentials from secrets file
		r = re.compile(r'^'+dbname+'\t')
		f = open(dbs_config, 'r')
		while True:
			line = f.readline().rstrip('\n')
			if not line:
				raise "Could not find db configuration"
			if r.search(line) is not None:
				self.dbname = dbname
				c=re.split("\t+",line)
				self.dbcredentials={
					"host": "localhost",
					"port": "33069",
					"user": c[3],
					"password": c[4],
					"database": dbname
				}
				break
		print("DB CONFIG for ", dbname, ": ", self.dbcredentials)
		self.db = mysql_connect_or_die(**self.dbcredentials)

	def ensureDB(self):
		if self.db is None:
			self.db=mysql_connect_or_die(**self.dbcredentials)

	def tables(self):
		cursor = self.db.cursor()
		cursor.execute("SHOW TABLES") 
		return list(map(lambda t: t[0], cursor.fetchall()))

	def fields(self, tname):
		sql = "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='%s' AND `TABLE_NAME`='%s'" 
		cursor = self.db.cursor()
		cursor.execute(sql % (self.dbname, tname))
		return list(map(lambda n: n[0], cursor.fetchall()))

	def search1(self, tables, first_name, last_name, email, sciper):
		self.ensureDB()

		cursor2 = self.db.cursor(dictionary=True, buffered=True)
		cursor3 = self.db.cursor(dictionary=True, buffered=True)

		data={}

		# return a list of dictionaries (each with different keys)
		hdata=[]		
		for table_name, table_columns in tables.items():
			sql="SELECT {} from {} where sciper={}".format("sciper,"+(",".join(table_columns)), table_name, sciper)
			cursor3.execute(sql)
			records = cursor3.fetchall()
			if (len(records)>0):
				print ("--- Table: {} found {} records".format(table_name, len(records)))
				for row in records:
					print(row)
					row['table']=table_name
					hdata.append(row)
			else:
				print ("--- Table: nothing found")

		return hdata

	# return a list of {dbname: xx, tablename: xx, filedname: xx, value: xx}
	def search2(self, email, sciper):
		ret = []
		self.ensureDB()
		tables = self.tables()
		for t in tables:
			field_values = [("mail", email), ("email", email), ("e-mail", email), ("sciper", str(sciper)) ]
			cols = self.fields(t)
			for (fn, fv) in field_values:
				if fn in cols:
					cursor = self.db.cursor(dictionary=True)
					# sql="SELECT * from " + t + " where %s = %s"
					# cursor.execute(sql, [fn, fv])
					sql="SELECT * from " + t + " where %s = '%s'"
					cursor.execute(sql % (fn, fv))
					lines = cursor.fetchall()
					if len(lines) > 0:
						for l in lines:
							for k, v in l.items():
								if v != None:
									ret.append({'db': self.dbname, 'table': t, 'field': k, 'value': v})
		return ret

class PeopleGDPR:
	def __init__(self):
		self.settings = settings['people']
		# self.dbs = map(lambda n: PeopleDB(n, self.settings['dbs_config']), self.settings['dbnames']) 
		self.dbs = []
		for n in self.settings['dbnames']:
			db = PeopleDB(n, self.settings['dbs_config'])
			self.dbs.append(db)

	def __str__():
		# TODO
		ret = ""
		return(ret)		

	def data_for_csv():
		# TODO
		return

	def searchDB(self, first_name, last_name, email, sciper):
		# print(self.dbs[0].tables())
		ret=[]
		for db in self.dbs:
			ret += db.search2(email, sciper)
		return ret

	def searchLogs(self, first_name, last_name, email, sciper):
		#                   ^.*? ([\d.]+) - - \[(.*?)\] "GET \/stefan\.peters/edit(.*?)" (\d+) (-|\d+) "(.*?)" .*$
		# re1 = re.compile('^.*? ([\\d.]+) - - \\[(.*?)\\] "GET /{}\.{}/edit(.*?)" (\\d+) (-|\\d+) "https://tequila.epfl.ch/(.*?)" .*$'.format(first_name.lower(), last_name.lower()))
		re1 = re.compile('^.*? ([\\d.]+) - - \\[(.*?)\\] "GET /{}\.{}/edit.*?" (\\d+) (-|\\d+) "https://tequila.epfl.ch/.*?" .*$'.format(first_name.lower(), last_name.lower()))
		print(re1)
		iplist={}
		logfile_events=[]
		site_interactions=[]
		for server in self.settings['servers']:

			# Check when user did login into people
			# cmd = "cd {} ; for f in access.log-*.gz ; do echo \"---- $f\"; zcat $f | grep -i \"{}.{}\" | grep tequila ; done".format(self.settings['log_dir'], first_name, last_name)
			# ret = subprocess.run(["/usr/bin/ssh", server, cmd], stdout=subprocess.PIPE)
			# First cache log files locally to avoit extra load to the server
			logdir = "data/people/logs/{}/".format(re.sub("^.*@|\..*$", "", server))
			os.makedirs(logdir, exist_ok=True)
			print("Syncing logs for server {}".format(server))
			ret = subprocess.run(["/usr/bin/rsync", "-a", "{}:{}/access.log-*.gz".format(server,self.settings['log_dir']), "{}/".format(logdir)])
			print("Synced logs for server {} : return value: {}".format(server, ret))
			# for path in glob.glob("{logidr}/access.log-*.gz"):
			# for path in glob.glob(logdir + "access.log-20210314.gz"):
			for path in glob.glob(logdir + "access.log-*.gz"):
				print("Seraching {}".format(path))
				gz = gzip.open(path, 'rb')
				f = io.BufferedReader(gz)
				for line in f.readlines():
					# interesting log lines look like the following where the 
					# requests comes from an authentication in tequila. The
					# second one in particular because only the user can edit
					# its own profile (...more or less):
					# people.epfl.ch 128.178.25.30 - - [23/Apr/2021:16:08:55 +0200] "GET /ciccio.pasticcio HTTP/1.1" 200 22828 "https://tequila.epfl.ch/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0" 1 1342965
					# people.epfl.ch 128.179.255.41 - - [23/Apr/2021:14:02:05 +0200] "GET /ciccio.pasticcio/edit HTTP/1.1" 200 45342 "https://tequila.epfl.ch/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0" 1 1876092
					m=re1.match(line.decode('utf-8'))
					if m is not None:
						print("match: ", m)
						g=m.groups()
						# add source ip address to list of possible IPs
						iplist[g[0]] = 1
						logfile_events.append({'comment': 'login for edit', 'from': g[0], 'ts': g[1]})

				gz.close()
		iplist=list(iplist.keys())
		print("iplist", iplist)
		iplistre="|".join(iplist).replace('.', '\.')
		re2 = re.compile('^.*? ({}) - - \[(.*?)\] "(.*?)" .*$'.format(iplistre))
		print(re2)
		for server in self.settings['servers']:
			logdir = "data/people/logs/{}/".format(re.sub("^.*@|\..*$", "", server))
			# for path in glob.glob(logdir + "access.log-20210314.gz"):
			for path in glob.glob(logdir + "access.log-*.gz"):
				gz = gzip.open(path, 'rb')
				f = io.BufferedReader(gz)
				for line in f.readlines():
					m=re2.match(line.decode('utf-8'))
					if m is not None:
						print("match: ", m)
						g=m.groups()
						# register possible access from given IP
						logfile_events.append({'comment': 'possible website interaction', 'server': server, 'from': g[0], 'ts': g[1], 'request': g[2]})
		return logfile_events

if __name__ == '__main__':

	s=PeopleGDPR()

	input_data = read_data("./data.yml")

	for user in input_data:
		udir="Results/{}".format(user['sciper'])
		if not os.path.exists(udir):
		    os.makedirs(udir)
		print_header(**user)
		data = s.searchDB(**user)
		keys=common_keys(data)
		keys.remove('table')
		keys.insert(0, 'table')
		write_csv('{}/peopleDB.csv'.format(udir), data, keys)

		data=s.searchLogs(**user)
		write_csv('{}/peopleAccessLogs.csv'.format(udir), data)
