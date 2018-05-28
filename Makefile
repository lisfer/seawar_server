run:
	export FLASK_APP=main; ./venv/bin/flask run --reload --debugger

heroku:
	export FLASK_APP=main; \
	flask run -h 0.0.0.0 -p $(PORT) --reload
