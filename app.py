from flask import Flask, render_template, request
from Bio import SeqIO
from matplotlib import use; use( 'Agg' ) # this is necessary for Flask, has to come before pyplot import
import matplotlib.pyplot as plt
import pandas
import uuid
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'] )
def index():
    if request.method == 'GET':
        return render_template( 'index.html' )
    elif request.method == 'POST':
        # get data from form

        job_id = uuid.uuid1()
        raw_fasta = request.form.get( 'fasta' )
        benchmark_check = request.form.get( 'benchmark_check' )

        # do things with form data

        # collect all the things we want to pass to template as Python objects
        results = {
            'job_id': job_id,
            'templates': [],
            'name': None,
            'original_input': raw_fasta,
        }

        # return rendered results template
        return render_template( 'results.html', results=results )

@app.route('/job/<job_id>', methods=['GET', 'POST'] )
def show_job( job_id ):
    if len( job_id ) == 36: # crude way of checking if it's a valid job ID
        if request.method == 'GET':
            # we want to see how this job is doing
            status = None
            results = {
                'job_id': job_id,
                'status': status,
            }
            return render_template( 'job.html', results=results )
        elif request.method == 'POST':
            # we want to post a job to the server
            # not sure if this would be at all useful
            return None

if __name__ == '__main__':
  app.run( debug=True ) # this is only for testing, it will break WSGI deployment


# code from fitter.py
# import pandas
# import datetime
#
# from numpy import diag, sqrt, linspace
# from scipy.optimize import curve_fit
#
# from matplotlib import use; use( 'Agg' )
# import matplotlib.pyplot as plt
#
# from StringIO import StringIO

# clean_dat = request.form.get( 'data' ).replace('Max V [420]', 'rate').replace(' ', '\n').lower()
# df = pandas.read_csv( StringIO( clean_dat ), sep='\t' )
#
# # map the form values to the DataFrame
# samplemap = { str(i+1): request.form.get( 'mut{}-name'.format( (i/3)+1 ) ) for i in range(12) }
#
# # save this data set
# df.to_csv( 'saved_runs/submitted_{}.csv'.format( datetime.datetime.now() ) )
#
# # group df by sample
# grouped = df.groupby( 'sample', sort=False )
# samples = [ ]
#
# # iterate over 4 samples by name, in entered order (see sort=False above)
# for name, df in grouped:
