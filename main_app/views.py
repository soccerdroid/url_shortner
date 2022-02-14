from distutils.errors import CompileError
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import redis
import hashlib

# Global variables
redis_instance_users = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
redis_instance_urls = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=1)   

CHAR_LENGTH = 8 #fixed length for short urls

# -----------Helper functions--------------
def generateShortUrl(email,url):
    '''
    Function that receives an email of a user and a URL and hashes it, to generate 
    a shorter version of the URL. If the email parameter == -1, it means that the user
    did not write any email.
    '''
    if(email=='-1'):
        return None
    compound_url = email+url
    hash_object = hashlib.sha512(compound_url.encode())
    hash_hex = hash_object.hexdigest()
    return (settings.HOSTNAME +'/'+hash_hex[0:CHAR_LENGTH])

def isUser(email):
    '''
    Function that receives an email and checks if the user exists in our db.
    '''
    if(email=='-1'):
        return False
    is_in_db = redis_instance_users.exists(email)
    return is_in_db


def getLongUrlDB(short_url):
    '''
    This function receives a short url and lookup in Redis to retrieve the associated
    long URL (the original URL). If the URL parameter == -1, it means that the user did 
    not write any URL.
    '''
    if(short_url=='-1'):
        return "URL is incorrect, please try again"
    return redis_instance_urls.hget(short_url, 'complete_url')
    

# -------Endpoints-----------

def get_short_url(request):
    '''
    This service receives a long url and email for authentication.
    It returns:
    - it's a POST request and if the user does not exist, returns a bad HTTP response.
    - If the user exists, and if it's a POST request, returns the shortened version of 
    the URL.
    - If it's a GET request, it displays a form where the email and the long URL are 
    asked.
    '''
    redis_instance_users.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})

    if(request.method == 'POST'):
        user_email = request.POST.get("email", "-1") 
        # We first check if the user is part of our system
        if(isUser(user_email)):
            complete_url = request.POST.get("complete_url", "-1")
            # Get the number of urls inserted by this user
            inserted_urls = redis_instance_users.get(user_email).decode('utf-8')
            # Generate a short version of the url
            new_short_url = generateShortUrl(user_email, complete_url)
            # Then, check if the short url already exists in the db
            short_url = redis_instance_urls.exists(new_short_url) if new_short_url else False
            if(short_url):
                # If true, we just display the short url
                return render(request, 'main_app/show_short_url.html',{'short_url':new_short_url, 'inserted_urls':inserted_urls})
            else:
                # Add the new short url to the db in the form short_url=>{complete_url, requests}
                redis_instance_urls.hmset(new_short_url,{'complete_url':complete_url, 'requests':1})

                # Also save the complete_url=>short_url pair for reverse lookup
                # redis_instance_urls.set(complete_url,new_short_url)

                # And increment the counter of the number of inserted urls by this user
                redis_instance_users.incr(user_email)
                # Get the number of urls inserted by this user
                inserted_urls = redis_instance_users.get(user_email).decode('utf-8')
                # Show both the new short url and the number of short urls inserted
                return render(request, 'main_app/show_short_url.html',{'short_url':new_short_url, 'inserted_urls':inserted_urls})
        else:
            return HttpResponseBadRequest("Not a user")
    
    return render(request, 'main_app/get_short_url.html',{})

def get_long_url(request):
    '''
    This service receives a short url. It returns the complete and original url 
    (if the short url exists in our db). Also, it will increment in our db the counter 
    of the number of requests that this short_url has received. Else, it returns a bad 
    HTTP response (bad request).
    '''
    if(request.method == 'POST'):
        short_url = request.POST.get("short_url", "-1")
        # Check if there exists a long URL associated to this short URL
        long_url = getLongUrlDB(short_url)
        if(long_url):
            # Increment the number of requests of this short url by 1
            redis_instance_urls.hincrby(short_url,'requests',1)
            # Get the number of requests this short URL has received
            requests = redis_instance_urls.hget(short_url, 'requests').decode('utf-8')
            # And display both the original URL and the number of requests
            return render(request, 'main_app/show_long_url.html',{'long_url':long_url.decode('utf-8'), 'requests': requests})
        else:
            return HttpResponseBadRequest("There ir no URL associated to this short URL.")
    return render(request, 'main_app/get_long_url.html',{})
