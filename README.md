# **Coursework on Informational systems and networks. Fall, 2021**

## Nikita Teterin

## **Stage 0**

+ Get familiar with `Flask`, `jinja` templating and revise HTTP
+ Add `static` and `templates` folders
+ Add simple script displaying current time and a bit of css
+ Add icon to the app

## **Stage 1**

+ Install MySQL server and setup database from last term
+ Implement simple `Connection` class using `pymysql`
+ Ensure connection succeded, put debug info to `.log` file

## **Stage 2**

+ Make first blueprint, separate resources and routes

## **Stage 3**

* Make second blueprint, add routes for main app
* Update `database` package, move `db-config.json` to the root of the project
* Setup new database on MySQL server

## **Stage 4**

+ Add `auth` blueprint, utilize Flask's `session`, create dummy policies
+ Play with templates, get used to `redirect` and `url_for`
+ Refactor project structure, move `json` configs to a single folder for `db` and `policies`

## **Stage 5**

+ Make advanced use of `Jinja`: chain templates for menus and header
+ Implement new model interface for queries with parameters
+ Implement `Validator` class to check user input when modifying the tables
+ Use `Bootstrap` for neater styling

## **Stage 6**

+ add `Dockerfile` and `.yml` for Docker-compose
+ add `.env/` dir with environmental variables for container
+ add `json` with config for dockerized application (change DB server hostname)
