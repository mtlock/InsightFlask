from flask import render_template, request,Response
from flaskexample import app
#from sqlalchemy import create_engine
#from sqlalchemy_utils import database_exists, create_database
import pandas as pd
#import psycopg2
#from a_Model import ModelIt
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import os.path
import numpy as np
#user = 'Mike' #add your username here (same as previous postgreSQL)                      
#host = 'localhost'
#dbname = 'ElectionTweets'
#db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
#con = None
#con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")



def root_dir():  # pragma: no cover
    #print os.path.realpath(__file__)
    print os.path.dirname(os.path.realpath(__file__))
    return os.path.dirname(os.path.realpath(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

@app.route('/Image/Moving.gif')
def get_image():
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join(root_dir(), '/Image/Moving.gif')
    complete_path = root_dir() + '/Image/Moving.gif'
    print complete_path
    ext = os.path.splitext('/Image/Moving.gif')[1]
    mimetype = mimetypes.get(ext, "tex")
    content = get_file(complete_path)
    return Response(content,mimetype='image/gif')


@app.route('/Image/Hashtag.gif')
def get_hashtag_image():
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join(root_dir(), '/Image/Hashtag.gif')
    complete_path = root_dir() + '/Image/Hashtag.gif'
    print complete_path
    ext = os.path.splitext('/Image/Hashtag.gif')[1]
    mimetype = mimetypes.get(ext, "tex")
    content = get_file(complete_path)
    return Response(content,mimetype='image/gif')



    
    
    
@app.route('/HashtagActivity')
def HashtagActivity():        
    return render_template("HashtagActivity.html")     

@app.route('/Hashtags')
def Hashtags():
    #pull start date/time and length of window and store it
    StartDay = request.args.get('start_day')
    StartHour = request.args.get('start_hour')
    StartMin = request.args.get('start_minute')
    AM_PM = request.args.get('am/pm')
    #Start time
    start_time = parser.parse(StartDay +' '+ StartHour+':'+StartMin+' '+AM_PM)

    AddDay = request.args.get('add_day')
    AddHour = request.args.get('add_hour')
    AddMin = request.args.get('add_minute') 
    #Finish time
    end_time = start_time + timedelta(days = int(AddDay)) + timedelta(hours = int(AddHour)) + timedelta(minutes = int(AddMin))
    
    start_date_limit = parser.parse('September 24 2:25 PM')
    end_date_limit = parser.parse('September 28 11:25 AM')

    
    if end_time == start_time or end_time > end_date_limit or start_time < start_date_limit:
        return render_template("BadDateRange_hashtags.html")
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns  
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        from matplotlib.dates import DateFormatter 
        from StringIO import StringIO
        import base64
        import io
        from io import BytesIO 
        import urllib
        import pickle
        from collections import Counter
        f = open('flaskexample/static/df_minute_hashtag_count.pickle', 'rb')
        df = pickle.load(f)
        f.close()
  
        ##############
        temp = df[(df.index <= end_time) & (df.index >= start_time)]
        D = {}
        for i in xrange(len(temp)):
            Temp_D = dict(df.iloc[i])
            for item in Temp_D:
                D[item] = D.get(item,0)+Temp_D[item]
        L = Counter(D).most_common(20)
        A=pd.DataFrame(dict(L),index=[1])
        A = A.transpose()
        
      
  
  
        fig=plt.figure()
        
        ax = fig.add_subplot(1, 1, 1)
        #plt.title('Number of tweets with each hashtag between '+str(start_time)+' and '+str(end_time))
        #ax.set_xlabel('Number of tweets with each hashtag between '+str(start_time)+' and '+str(end_time))
        A.plot.barh(ax=ax,x=A.index, y=1, legend=False)
        
        io = StringIO()
        fig.savefig(io, format='png')
        data = base64.encodestring(io.getvalue())
        
        data=urllib.quote(data.rstrip('\n'))
        return render_template("HashtagOutput.html", png = data,start_time = start_time.strftime('%m/%d/%Y %I:%M%p'),end_time=end_time.strftime('%m/%d/%Y %I:%M%p'))
  
  
@app.route('/input')
def find_tweets_input():
    return render_template("input.html")


@app.route('/output')
def find_tweets_output():
    #pull 'birth_month' from input field and store it
  tag = request.args.get('hashtag')
    #just select the Cesareans  from the birth dtabase for the month that the user inputs
  query = "SELECT index, text, single_hashtag FROM simple_processed_one_hashtag_table WHERE single_hashtag = '%s'" % tag
  print query
  query_results=pd.read_sql_query(query,con)
  print query_results
  tweets = []
  for i in range(0,query_results.shape[0]):
      tweets.append(dict(index=query_results.iloc[i]['index'], text=query_results.iloc[i]['text'], hashtag=query_results.iloc[i]['single_hashtag']))
  the_result = ModelIt(tag,tweets)
  return render_template("output.html", tweets = tweets, the_result = the_result)
  
  

@app.route('/TweetData')#,methods = ['GET','POST'])
def TweetData():
    #if request.method == 'POST':
        
    return render_template("TweetData.html")
    
    
    
@app.route('/graph')
def graph():
    #pull start date/time and length of window and store it
    StartDay = request.args.get('start_day')
    StartHour = request.args.get('start_hour')
    StartMin = request.args.get('start_minute')
    StartAM_PM = request.args.get('start_am/pm')
    #Start time
    start_time = parser.parse(StartDay +' '+ StartHour+':'+StartMin+' '+StartAM_PM)

    EndDay = request.args.get('end_day')
    EndHour = request.args.get('end_hour')
    EndMin = request.args.get('end_minute')
    EndAM_PM = request.args.get('end_am/pm')
    #End time
    end_time = parser.parse(EndDay +' '+ EndHour+':'+EndMin+' '+EndAM_PM)
    
    start_date_limit = parser.parse('September 24 2:25 PM')
    end_date_limit = parser.parse('September 28 11:25 AM')
    
    #Time blocks
    time_block = request.args.get('time_block')
    time_block = int(time_block)
    
    if end_time <= start_time or end_time > end_date_limit or start_time < start_date_limit:
        return render_template("BadDateRange.html")
    elif time_block == 0:
        return render_template("BadDateRange_time_block.html")
    
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns  
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        from matplotlib.dates import DateFormatter 
        from StringIO import StringIO
        import base64
        import io
        from io import BytesIO 
        import urllib
        import pickle
        
        f = open('flaskexample/static/df_minute_tweet_count.pickle', 'rb')
        df = pickle.load(f)
        f.close()

        ##############
        Array = []
        begin_time = start_time
        while begin_time <= end_time - timedelta(minutes=time_block):
            finish_time = begin_time + timedelta(minutes = time_block)
            temp_info = [finish_time]
            temp_df = df[(df.index>= begin_time) & (df.index < finish_time)]
            # Clinton count
            temp_info.append(np.sum(temp_df['Pro Clinton / Anti Trump']))
            # Trump count
            temp_info.append(np.sum(temp_df['Pro Trump / Anti Clinton']))
    
            Array.append(temp_info)
            begin_time = finish_time
        Array = np.array(Array)
        Graph_df = pd.DataFrame(Array,columns = ['Time','Pro-Clinton / Anti-Trump','Pro-Trump / Anti-Clinton'])
        Graph_df = Graph_df.set_index('Time')
        ###############
        fig=plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        Graph_df.plot(ax=ax,colors=['b','r'])
        title = 'Tweet activity from ' + start_time.strftime('%m/%d/%Y %I:%M%p') + ' to ' + end_time.strftime('%m/%d/%Y %I:%M%p')
        y_label = '# of Tweets in previous ' + str(time_block)+' minutes'
        plt.ylabel(y_label)
        plt.xlabel('Time')  
        plt.title(title)
        io = StringIO()
        fig.savefig(io, format='png')
        data = base64.encodestring(io.getvalue())
        data=urllib.quote(data.rstrip('\n'))
        return render_template("GraphOutput.html", png = data)


  
@app.route('/HashtagEvolution')
def HashtagEvolution():        
    return render_template("HashtagEvolution.html")     

@app.route('/TagEvolution')
def TagEvolution():
    #pull start date/time and length of window and store it
    hashtag1 = request.args.get('hashtag_1')
    hashtag2 = request.args.get('hashtag_2')
    hashtag3 = request.args.get('hashtag_3')
    hashtag4 = request.args.get('hashtag_4')
    L = [hashtag1,hashtag2,hashtag3,hashtag4]
    Use = [x for x in L if len(x)>0]
    if len(Use) == 0:
        return render_template("BadHashtagEvolution.html")
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns  
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.figure import Figure
        from matplotlib.dates import DateFormatter 
        from StringIO import StringIO
        import base64
        import io
        from io import BytesIO 
        import urllib
        import pickle
    
        f = open('flaskexample/static/df_hashtag_evolution.pickle', 'rb')
        df = pickle.load(f)
        f.close()
        
        fig=plt.figure()
        #ax = fig.add_subplot(1, 1, 1)
        #ax = df[Use].plot()
        #ax.set_ylim(0,1)
        #plt.ylabel('Daily probability')
        #plt.title('Probabilistic classification of hashtags in the Pro-Clinton / Anti-Trump camp')
    
        ax = fig.add_subplot(1, 1, 1)
        ax.set_ylim(0,1)
        df[Use].plot(ax=ax) 
        plt.ylabel('Daily probability') 
        plt.title('Probabilistic classification of hashtags in the Pro-Clinton / Anti-Trump camp')
    
        io = StringIO()
        fig.savefig(io, format='png')
        data = base64.encodestring(io.getvalue())
        data=urllib.quote(data.rstrip('\n'))
        return render_template("HashtagEvolutionOutput.html", png = data)
  