from flask import Flask, render_template, request
from Bio import SeqIO
from matplotlib import use; use( 'Agg' ) # this is necessary for Flask, has to come before pyplot import
import matplotlib.pyplot as plt
import pandas
import uuid
from modules.seq import hmmerapi
#import StringIO
from cStringIO import StringIO

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
        fastainput = StringIO(raw_fasta)

        ## Read the raw fasta into a biopython seqio object
#        myseq = SeqIO.to_dict( SeqIO.parse( fastainput, 'fasta' ))  #this is for multiple sequences
        myseq = SeqIO.read(fastainput,'fasta')
        ## Now that we have the input target sequence,
        ## we should check to see if it's stored in any of the json output
        ## Ie, why run again if we've already got the results
        ## mostly for debugging

        jsonhits = hmmerapi.run_phmmer( myseq, 'pdb' )

        records = SeqIO.to_dict( hmmerapi.remove_dup_seqs( SeqIO.parse('pdb', 'fasta')) )

        for i in records:
            print i
            print list(i)

        mytemplateresults = []
        for i in range(0,len(jsonhits['results']['hits'])):
            mypdbcode = str(jsonhits['results']['hits'][i]['acc'] )
            try:
                mytemplateresults.append( { 'name': mypdbcode,
                                            'seq': str(records[mypdbcode].seq),
                                            'pid': " Not Calc Yet",
                                            'idx':i,
                                        } )

            except:
                mytemplateresults.append( { 'name': mypdbcode,
                                            'seq': 'NA',
                                            'pid': " Not Calc Yet",
                                            'idx':i,
                                        } )

        print mytemplateresults
#need to read in the full fasta to get the sequence of the hit
# this should actually just be lazy loaded post template selection 
#            mytemplateresults['seq'] = 
        # collect all the things we want to pass to template as Python objects
        results = {
            'Total Number of Hits': len(jsonhits['results']['hits']),
            'job_id': job_id,
            'templates': mytemplateresults,
#how to i add shit to the templates???? fucking html
#            'hmmer jobid' : jsonhits['results']['uuid'],
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
