import csv
import glob
import logging
import mysql.connector
import re
import subprocess
import yaml 

from common import *

class WikiGDPR:
	def __init__(self):
		self.settings = settings['wiki']
		self.db=mysql_connect_or_die(**self.settings['db'])
		self.last_search_data={}

		self.fieldnames = [
			"first_name", "last_name", "email", "sciper", 
			"Wikis as administrator", "Wikis as editor", "Wikis as reader", "Wikis as subscriber", 
			"Wiki Articles as owner", "Wiki Comments as owner", 
			"Title of Wikis as administrator", "Title of Wikis as editor", "Title of Wikis as reader", "Title of Wikis as subscriber"
		]
	
	def __str__():
		# TODO
		ret = ""
		return(ret)		

	def data_for_csv():
		# TODO
		return

	def search(self, first_name, last_name, email, sciper):
		cursor2 = self.db.cursor(dictionary=True, buffered=True)
		cursor3 = self.db.cursor(dictionary=True, buffered=True)

		data={}

		print("\n-------------------------------------------- Infos as PolyWiki user")

		NAMES = {
			"ch.epfl.kis.polywiki.model.Wiki":    "Wikis",
		}
		sql="SELECT businessObjectClassName as t,role,COUNT(1) as n FROM objectRole WHERE  principalName = {} OR principalLabel LIKE '%{}%{}%' GROUP BY t".format(sciper, first_name, last_name)
		cursor3.execute(sql)
		for row in cursor3:
			t=NAMES[row['t']]
			print("{} of {} {}".format(row['role'].capitalize(), row['n'], t))
			data["{} as {}".format(t, row['role'])] = row['n']

			if t=="Wikis":
				sql="SELECT wiki.id,wiki.label from objectRole INNER JOIN wiki ON objectRole.businessObjectId = wiki.id where (objectRole.principalName={} OR objectRole.principalLabel = '{} {}') AND objectRole.businessObjectClassName='ch.epfl.kis.polywiki.model.Wiki' AND objectRole.role='{}'".format(sciper, first_name, last_name, row['role'])
				cursor2.execute(sql)
				tt=[]
				for row2 in cursor2:
					print("    title: '{}'\n    user: {}/{}\n".format(row2['label'], row2['principalName'], row2['principalLabel']))
					tt.append("'{}'".format(row2['label']))
				data["Title of Wikis as {}".format(row['role'])]=" - ".join(tt)

		sql="SELECT COUNT(1) as c FROM subscription WHERE email = '{}'".format(email)
		cursor3.execute(sql)
		row=cursor3.fetchone()
		c = row['c']
		print("Subscribed to {} wikis".format(c))
		if c > 0:
			data["Wikis as subscriber"] = c
			sql="SELECT wiki.id,wiki.label from subscription INNER JOIN wiki ON subscription.wikiId = wiki.id where subscription.email = '{}'".format(email)
			cursor2.execute(sql)
			tt=[]
			for row2 in cursor2:
				print("    title: '{}'".format(row2['label']))
				tt.append("'{}'".format(row2['label']))
			data["Title of Wikis as subscriber"]=" - ".join(tt)


		sql="SELECT count(1) as c FROM page WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
		cursor3.execute(sql)
		row=cursor3.fetchone()
		print("Pages as author: {}".format(c))
		if c > 0:
			sql="SELECT * FROM page WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
			cursor2.execute(sql)
			tt=[]
			for row2 in cursor2:
				print("    from {} as {}/{} page title: '{}'\n    content: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['title'], row2['content']))
				tt.append(print("From IP {} as {}/{} page title: '{}'; page content: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['title'], row2['content'])))
			data["Pages as editor"]="\n".join(tt)

		sql="SELECT count(1) as c FROM pageArchive WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
		cursor3.execute(sql)
		row=cursor3.fetchone()
		print("Pages from archive as user: {}".format(c))
		if c > 0:
			sql="SELECT * FROM pageArchive WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
			cursor2.execute(sql)
			tt=[]
			for row2 in cursor2:
				print("    from {} as {}/{} page title: '{}'\n    content: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['title'], row2['content']))
				tt.append(print("From IP {} as {}/{} page title: '{}'; page content: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['title'], row2['content'])))
			data["Pages from archive as editor"]="\n".join(tt)

		sql="SELECT count(1) as c FROM comment WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
		cursor3.execute(sql)
		row=cursor3.fetchone()
		print("Comments as author: {}".format(c))
		if c > 0:
			sql="SELECT * FROM comment WHERE `userLabel` LIKE '%{}%{}%'".format(first_name, last_name)
			cursor2.execute(sql)
			tt=[]
			for row2 in cursor2:
				print("    from {} as {}/{}. Comment: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['content']))
				tt.append(print("From IP {} as {}/{}, comment: '{}'".format(row2['footprint'], row2['userId'], row2['userLabel'], row2['content'])))
			data["Comments as author"]="\n".join(tt)

		return(data)

if __name__ == '__main__':

	s=WikiGDPR()

	input_data = read_data("./data.yml")
	output_data=[]
	for user in input_data:
		print_header(**user)
		d=s.search(**user)
		for k, v in user.items():
			d[k] = v
		output_data.append(d)

	fieldnames=s.fieldnames

	with open('wiki.csv', 'w') as csvfile:
		w = csv.DictWriter(csvfile, fieldnames=fieldnames, restval="")
		w.writeheader()
		for d in output_data:
			w.writerow(d)