from flask import Flask, render_template, request, session
from Bio import SeqIO
from matplotlib import use; use( 'Agg' ) # this is necessary for Flask, has to come before pyplot import
import matplotlib.pyplot as plt
import pandas
import uuid
from modules.seq import hmmerapi
import requests
from cStringIO import StringIO
import os
import json

app = Flask(__name__)
app.secret_key = 'oh_so_secret!'

@app.route('/', methods=['GET', 'POST'] )
def index():
    if request.method == 'GET':
        return render_template( 'index.html' )
    elif request.method == 'POST':

        # get data from form
        job_id = uuid.uuid1()
        raw_fasta = request.form.get( 'fasta' )
        benchmark_check = request.form.get( 'benchmark_check' )
        my_seq = StringIO( raw_fasta )
        my_seq = SeqIO.read( my_seq, 'fasta' )

        # submit request to hmmer
        url = 'http://www.ebi.ac.uk/Tools/hmmer/search/phmmer?&seqdb=pdb&seq=>{}%0A{}'.format( 'name', my_seq.seq )
        r = requests.post( url )

        for key in r.keys():
            print r[ key ]

        job_id = r.headers
        d_url = 'http://www.ebi.ac.uk/Tools/hmmer/download/{}/score?&format=fullfasta'.format( job_id )
        g = requests.get( d_url )

        # # mostly for debugging
        # if os.path.isfile( 'pdb.json' ):
        #     print "Using previous, this is just for testing!"
        #     f = open( 'pdb.json', 'r' )
        #     hits = json.load( f )
        # else:

#         hits = hmmerapi.run_phmmer( myseq, 'pdb' ) #writes pdb* files to disk
#         records = SeqIO.to_dict( hmmerapi.remove_dup_seqs( SeqIO.parse( 'pdb', 'fasta' ) ) )
#
#         # for i in records:
#         #     print i
#         #     print list(i)
#
#         print records
#
#         mytemplateresults = []
#         for i in range(0,len(jsonhits['results']['hits'])):
#             mypdbcode = str(jsonhits['results']['hits'][i]['acc'] )
#             try:
#                 mytemplateresults.append( { 'name': mypdbcode,
#                                             'seq': str(records[mypdbcode].seq),
#                                             'pid': " Not Calc Yet",
#                                             'idx':i,
#                                         } )
#
#             except:
#                 mytemplateresults.append( { 'name': mypdbcode,
#                                             'seq': 'NA',
#                                             'pid': " Not Calc Yet",
#                                             'idx':i,
#                                         } )
#
#         results = {
#             'total_hits': len(jsonhits['results']['hits']),
#             #'job_id': job_id,
#             'templates': mytemplateresults,
#             'hmmer_jobid' : jsonhits['results']['uuid'],
#             'name': None,
#             'original_input': raw_fasta,
#         }
#
#         # add JSON object to session dict
#         session['data'] = json.dumps( results )
#
#         # return rendered results template
#
# #        cleanup()
        #return render_template( 'results.html', results=results, session=session )
        return r.text

@app.route( '/templates', methods=['GET', 'POST'] )
def templates():
    if request.method == 'GET':
        return 'GET'

    elif request.method == 'POST':
        #session_data = json.loads( request.form.get( 'session_data' ) )
        raw_data = request.form.get( 'session_data' )
        j = json.loads( raw_data )

        print j.keys()

        picks = []
        for template in j['templates']:
            checked = bool( request.form.get( template['name'] ) )
            if checked:
                picks.append( template )

        picks_fasta = [ '>{}\n{}\n'.format( i['name'], i['seq'] ) for i in picks ]
        print picks_fasta
        with open( 'tmp.fasta', 'w' ) as fn:
            fn.write( ''.join( picks_fasta ) )

        return render_template( 'picks.html', picks=picks )


@app.route('/job/<job_id>', methods=['GET', 'POST'] )
def show_job( job_id ):
    if len( job_id ) == 36: # crude way of checking if it's a valid job ID
        if request.method == 'GET':
            # we want to see how this job is doing
            status = None
            results = {
                'job_id': job_id,
                'status': status,
                'json': json.load( 'static/jobs/{}'.format( job_id ) )
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

def cleanup():
    import os
    os.remove('pdb')
    os.remove('pdb.gz')
    os.remove('pdb.json')
