from distutils.errors import CompileError
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import redis
import hashlib

redis_instance_users = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
redis_instance_urls = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=1)                                 

def generateShortUrl(url, char_length = 8):
    hash_object = hashlib.sha512(url.encode())
    hash_hex = hash_object.hexdigest()
    return (settings.HOSTNAME +'/'+hash_hex[0:char_length])

def isUser(email):
    if(email=='-1'):
        return False
    is_in_db = redis_instance_users.exists(email)
    return is_in_db

def getShortUrlDB(url):
    if(url=='-1'):
        return "URL is incorrect, please try again"
    return redis_instance_urls.get(url)


def get_short_url(request):
    '''This service receives a long url and email for authentication.
    It returns:
    - it's a POST request and if the user does not exist, returns a bad HTTP response.
    - If the user exists, and if it's a POST request, returns the shortened version of the URL.
    - If it's a GET request, it displays a form where the email and the long URL are asked.
    '''
    redis_instance_users.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})

    if(request.method == 'POST'):
        user_email = request.POST.get("email", "-1") 
        # We first check if the user is part of our system
        if(isUser(user_email)):
            complete_url = request.POST.get("complete_url", "-1")
            short_url = getShortUrlDB(complete_url)
            # Then, check that the short url already exists in the db
            if(short_url):
                # This is to remove the b' prefix (bytes object)
                short_url = short_url.decode("utf-8")
                # If true, we just display the short url
                return render(request, 'main_app/show_short_url.html',{'short_url':short_url})
            else:
                # Generate a short version of the url
                new_short_url = generateShortUrl(complete_url)
                # Add the new short url to the db
                redis_instance_urls.hmset(new_short_url,{'complete_url':complete_url, 'requests':1})
                # Also save the complete_url=>short_url pair for reverse lookup
                redis_instance_urls.set(complete_url,new_short_url)
                # And increment the counter of the number of inserted urls by this user
                redis_instance_users.incr(user_email)
                return render(request, 'main_app/show_short_url.html',{'short_url':new_short_url})
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