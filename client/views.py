from django.http.response import HttpResponse
from django.views.generic import View
import tweepy
from django.template import Template, Context, loader
from django.shortcuts import redirect

consumer_token = 'zpoLczki1nN5RkZ8Ll0DKebXT'
consumer_secret = 'tOpkUB4OsmZAotkVX85VzEiJTY2YXwP14JXLacUl02BG0hOJJZ'
callback_url = 'https://quiet-springs-48027.herokuapp.com/login/'

class LoginUser(View):

    def post(self, request, *args, **kwargs):
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        try:
            redirect_url = auth.get_authorization_url()
            request.session['request_token'] = auth.request_token
            location = redirect_url
            res = HttpResponse(location, status=302)
            res['Location'] = location
            return res
        except tweepy.TweepError:

            print 'Error in login post! Failed to get request token.'


    def get(self, request, *args, **kwargs):
        if request.GET.get('oauth_verifier'):
            try:
                verifier = request.GET.get('oauth_verifier')
                auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
                auth.request_token = request.session['request_token']
                del request.session['request_token']
                auth.get_access_token(verifier)
                request.session['auth_access_token'] = auth.access_token
                request.session['auth_token_secret'] = auth.access_token_secret
                return redirect('/home/')
            except tweepy.TweepError:
                print 'Error in login get! Failed to get access token.'
        else:
            if request.session.get('auth_access_token') and request.session.get('auth_token_secret'):
                return redirect('/home/')
            else:
                login_temp = loader.get_template('login.html')
                return HttpResponse(login_temp.render({}))




class HomePage(View):

    def get(self, request, *args, **kwargs):
        '''
        post tweet, callback url for login
        '''
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(request.session['auth_access_token'], request.session['auth_token_secret'])
        api = tweepy.API(auth)
        user = api.get_user('twitter')
        context = {}
        context['username'] = user.screen_name
        context['tweets'] = api.user_timeline(user.screen_name)
        template = loader.get_template('tweet.html')
        c = Context(context)
        rendered = template.render(c)
        return HttpResponse(rendered)

    def post(self, request, *args, **kwargs):
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(request.session['auth_access_token'], request.session['auth_token_secret'])
        api = tweepy.API(auth)
        api.update_status(request.POST.get('tweet'))
        return redirect('/home/')