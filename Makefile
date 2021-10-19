all: up inform wiki

.PHONY: up
up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

.PHONY: inform
inform: settings.yml up
	PYTHONIOENCODING=utf8 python inform.py

.PHONY: blog
# blog is no longer active: no access to DB
# blog: settings.yml
# 	@echo "Remember to dig the tunnel first:"
# 	@echo "ssh -L 33066:127.0.0.1:3306 kis@kissrv93.epfl.ch" 
# 	python blog.py
blog:
	PYTHONIOENCODING=utf8 python blog_oc.py

.PHONY: wiki
wiki: settings.yml
	/bin/sh tunnel_wiki.sh start
	PYTHONIOENCODING=utf8 python wiki.py 
	/bin/sh tunnel_wiki.sh stop

.PHONY: people
people: settings.yml
	/bin/sh tunnel_people.sh start
	PYTHONIOENCODING=utf8 python people.py
# 	/bin/sh tunnel_people.sh stop

settings.yml: settings.yml.example
	touch settings.yml
	@echo "Please create settings.yml. Use settings.yml.example as an example"

clone:
	rsync -av inform:/var/log/httpd/inform.epfl.ch-access_log* data/mocs/
	ssh inform

data/inform.sql.gz:
	ssh inform "cd GiovaGDPR && ./dump.sh"
	scp inform:GiovaGDPR/inform.sql.gz $@

clonedb: data/inform.sql.gz up
	cat $< | gunzip | docker-compose exec -T db mysql -u root --password=ROOT inForm