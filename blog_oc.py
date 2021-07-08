import csv
import glob
import logging
import re
import subprocess
import yaml 

from common import *

class BlogGDPR:
	def __init__(self):
		self.settings = settings['blog']
		self.ks = self.settings['k8s']

		ret = subprocess.run([self.ks['oc'], 'project', self.ks['project']])
		ret = subprocess.run([self.ks['oc'], 'project'], stdout=subprocess.PIPE)
		out=ret.stdout.rstrip(b'\n').decode('utf-8')
		chk='Using project "{}" on server "{}".'.format(self.ks['project'], self.ks['server'])
		if (out != chk):
			raise AssertionError("Openshift project does not match")

		ret = subprocess.run([self.ks['bin'], 'get', 'pods', '-o', 'name'], stdout=subprocess.PIPE)
		self.pod = ret.stdout.rstrip(b'\n').decode('utf-8')
		print("POD name: {}".format(self.pod))

	def __str__():
		# TODO
		ret = ""
		return(ret)		

	def data_for_csv():
		# TODO
		return

	def search(self, first_name, last_name, email, sciper):
		# kubectl exec -it pod/blogs-9946646b5-fk72t -- ls
		cmd = 'cd /usr/local/apache2/htdocs/archive; grep -E -r --exclude-dir=TRASHBIN --exclude-dir=EXPORTED -e "{}|{}|{}.*{}" *'.format(sciper, email, first_name, last_name)
		ret = subprocess.run([self.ks['bin'], 'exec', '-it', self.pod, '--', '/bin/sh', '-c', cmd], stdout=subprocess.PIPE)
		print(ret.stdout)
		data=ret.stdout
		return(data)

if __name__ == '__main__':

	s=BlogGDPR()
	exit

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