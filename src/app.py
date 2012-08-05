import os

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for

import simplejson
import urllib2

app = Flask(__name__)
app.jinja_env.trim_blocks = True

MAX_TWEETS = 1000
INCLUDE_RETWEETS = True
EXCLUDE_REPLIES = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        redirect_to = url_for('tagcloud', twitterhandle=request.form['handle'])
        return redirect(redirect_to)
    else:
        return render_template('index.html')
    
@app.route('/tagcloud/<twitterhandle>', methods=['GET'])
def tagcloud(twitterhandle):
    num_words_grouped = read_tweets(twitterhandle,
                                    MAX_TWEETS,
                                    INCLUDE_RETWEETS,
                                    EXCLUDE_REPLIES)
    return render_template('tagcloud.html',
                           twitterhandle=twitterhandle,
                           number_of_tweets=sum(num_words_grouped.values()),
                           max_number_of_tweets = MAX_TWEETS,
                           include_retweets = INCLUDE_RETWEETS,
                           include_replies = not EXCLUDE_REPLIES,
                           num_words_grouped=num_words_grouped)

def read_tweets(twitterhandle,
                num_tweets, 
                include_retweets, 
                exclude_replies):
    url = "https://api.twitter.com/1/statuses/user_timeline.json?\
include_entities=false&trim_user=true&screen_name={}&include_rts={}\
&exclude_replies={}&count={}".format(twitterhandle, include_retweets,
                                         exclude_replies, num_tweets)
    
    f = urllib2.urlopen(url)     
    content = f.read()        
    js_tweets = simplejson.loads(content)
    
    num_words = [len(js_tweet['text'].split()) for js_tweet in js_tweets]
    num_words_grouped = {x:num_words.count(x) for x in set(num_words)}
    
    return num_words_grouped
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
