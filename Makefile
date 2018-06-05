all: inform blog

inform: settings.yml
	pipenv run python inform.py 

blog: settings.yml
	pipenv run python blog.py 

settings.yml: settings.yml.example
	touch settings.yml
	@echo "Please create settings.yml. Use settings.yml.example as an example"