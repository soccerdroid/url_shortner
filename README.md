# url_shortner
Project for the Distributed Systems for Massive Data Management course at Université Paris Saclay

Pre-requisites:
- Python 3.6 or above
- Django~=3.2.12
- redis (python client and a local installation or a docker container)

## Getting started
It is suggested to use a virtual environment. 
Create it:
```bash
python3 -m venv <name_you_wish>
```
And then activate it:
```bash
source <name_you_wish>/bin/activate
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all the pre-requisites. They are all enumerated in the requirements.txt file.
```bash
pip install -r requirements.txt
```
**NOTE**: if you have more than one version of python installed in your computer, make sure to use `python3` instead of `python` in all the commands. 

## Initial settings
In the file url_shortner_app/settings.py, you should change the variables
`REDIS_HOST` and `REDIS_PORT` according to where your redis service is running.

## Services
All the required services are located in the main_app/views.py file.
The available endpoints are:
- `localhost:8000/longurl/`
- `localhost:8000/shortenurl/`

This app uses db's 0 and 1 of Redis. 
- db 0: stores user_email:inserted_urls pairs. Example:
```bash
user@gmail.com 0
```
- db 1: stores short_url:{complete_url, requests} pairs, where complete_url is the original URL, and requests is the number of times this short_url has been requested. Example:
```bash
 ubly.com/acb367b3 {'complete_url': neopets.com, 'requests': 1}
```


## How to run the app
1. Make sure redis is running and that `REDIS_HOST` and `REDIS_PORT` variables are correctly filled.
2. Fill the Redis databases with some initial values, particularly, create some users in order to be able to use the `localhost:8000/shortenurl/` service:
```bash
redis-cli -n 0 # to connect to database 0, where users are stored
>set user@gmail.com 0 # this means user@gmail.com exists, but has not insertened any short url
```

```bash
redis-cli -n 1 # to connect to database 1, where short urls are stored
>hmset ubly.com/acb367b3 complete_url 'neopets.com' requests 0 # this means user@gmail.com exists, but has not insertened any short url
```

3. From the root directory, execute:
```bash
python3 manage.py runserver
```
The app will automatically run in localhost:8000/

