import csv
import glob
import logging
import mysql.connector
import re
import subprocess
import yaml 

from common import *

class BlogGDPR:
	def __init__(self):
		self.settings = settings['blog']
		self.db=mysql_connect_or_die(**self.settings['db'])
		self.last_search_data={}

		self.fieldnames = [
			"first_name", "last_name", "email", "sciper", 
			"Blogs as administrator", "Blogs as blogger", "Blogs as reader", "Blogs as subscriber", 
			"Blog Articles as owner", "Blog Comments as owner", 
			"Title of Blogs as administrator", "Title of Blogs as blogger", "Title of Blogs as reader", "Title of Blogs as subscriber"
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

		print("\n-------------------------------------------- Infos as PolyBlog user")

		NAMES = {
			"ch.epfl.kis.polyblog.model.Blog":    "Blogs",
			"ch.epfl.kis.polyblog.model.Article": "Blog Articles",
			"ch.epfl.kis.polyblog.model.Comment": "Blog Comments",
		}
		sql="SELECT businessObjectClassName as t,role,COUNT(1) as n FROM objectRole WHERE  principalName = {} OR principalLabel = '{} {}' GROUP BY t".format(sciper, first_name, last_name)
		cursor3.execute(sql)
		for row in cursor3:
			t=NAMES[row['t']]
			print("{} of {} {}".format(row['role'].capitalize(), row['n'], t))
			data["{} as {}".format(t, row['role'])] = row['n']

			if t=="Blogs":
				sql="SELECT blog.id,blog.label from objectRole INNER JOIN blog ON objectRole.businessObjectId = blog.id where (objectRole.principalName={} OR objectRole.principalLabel = '{} {}') AND objectRole.businessObjectClassName='ch.epfl.kis.polyblog.model.Blog' AND objectRole.role='{}'".format(sciper, first_name, last_name, row['role'])
				cursor2.execute(sql)
				tt=[]
				for row2 in cursor2:
					print("    title: '{}'".format(row2['label']))
					tt.append("'{}'".format(row2['label']))
				data["Title of Blogs as {}".format(row['role'])]=" - ".join(tt)

		sql="SELECT COUNT(1) as c FROM subscription WHERE email = '{}'".format(email)
		cursor3.execute(sql)
		row=cursor3.fetchone()
		c = row['c']
		if c > 0:
			print("Subscribed to {} blogs".format(c))
			data["Blogs as subscriber"] = c
			sql="SELECT blog.id,blog.label from subscription INNER JOIN blog ON subscription.blogId = blog.id where subscription.email = '{}'".format(email)
			cursor2.execute(sql)
			tt=[]
			for row2 in cursor2:
				print("    title: '{}'".format(row2['label']))
				tt.append("'{}'".format(row2['label']))
			data["Title of Blogs as subscriber"]=" - ".join(tt)

		return(data)

if __name__ == '__main__':

	s=BlogGDPR()

	input_data = read_data("./data.yml")
	output_data=[]
	for user in input_data:
		print_header(**user)
		d=s.search(**user)
		for k, v in user.items():
			d[k] = v
		output_data.append(d)

	fieldnames=s.fieldnames

	with open('blog.csv', 'w') as csvfile:
		w = csv.DictWriter(csvfile, fieldnames=fieldnames, restval="")
		w.writeheader()
		for d in output_data:
			w.writerow(d)