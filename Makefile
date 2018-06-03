run:
	export FLASK_APP=seawar_server; ./venv/bin/flask run --reload --debugger

heroku:
	export FLASK_APP=seawar_server; \
	flask run -h 0.0.0.0 -p $(PORT) --reload

deploy:
	git push heroku master