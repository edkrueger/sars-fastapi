# SARS-API

## Dev Instructions
Run `pipenv install --dev` to install the env.  
Run `pipenv run pre-commit install` to initialize the git hooks.  
Run `pipenv run pre-commit run --all-files` if there are file that were committed before adding the git hooks.  
Activate the shell with: `pipenv shell`  
Lint with: `pylint app` and `pylint load.py`

## Build and Run the App With Docker (Dev)
Run `docker-compose build` to build the containers.  
Run `docker-compose up` to start the app.  
Run `docker-compose up -d` to start the app in detached mode.  
Run `mysql -h 0.0.0.0 -P 53306 -u root -p database` (password) to dive into testing mysql container.  
Run `docker-compose down` to stop the app.
