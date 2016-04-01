__author__ = 'stevebertolani'
from os import path
import urllib2
import urllib
import gzip
import json
import subprocess
from re import search,compile
from Bio.SeqUtils.CheckSum import seguid
from Bio import SeqIO

# Below is a parser for the command line output from various hmmer and esl tools
# One for the esl-alipid
class AlipidLine(object):

    def __init__(self,line):
        line = line.rstrip('\n')
        myline = line.split()
        #assert len(line) == 5
        self.target = myline[0]
        self.name = myline[1]
        self.pid = float(myline[2])
        self.beginpos = int(myline[3])
        self.endpos = int(myline[4])
        self.pdb = False
        self.check_name()

    def check_name(self):
        mysplit = self.name.split('_')
        myreg = compile('[A-Z]')
        if len(mysplit) == 2:
            if len(mysplit[0]) ==4:
                if myreg.search( mysplit[1] ):
                    #print "This is probably a PDB code"
                    self.pdb = True

# install a custom handler to prevent following of redirects automatically.
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return headers

def run_phmmer(seq,database):
    '''
    Takes an input seqeunce and returns a json object from HMMER3 server
    

    :param seq: assumes is a bio.seqrecord
    :type seq: This is a bio.seqrecord sequence protein fasta
    :return json: Returns the hmmer json object
    
    :Example
    """ Give example here ;) """"

   '''
    mydatabase = database
    res_params ={'output':'json','range':'1,100'}                   # don't forget to grab search params                       
    json_file_name = "%s.%s" %(database,res_params['output'])


    print "Running a phmmer search on %s" %database
    method = "phmmer"

    search_params = {'seqdb':"%s" %database,'seq': ">%s\n%s" %(seq.id,seq.seq) }
    print "Using search parameters %s" %search_params

    opener = urllib2.build_opener(SmartRedirectHandler())
    urllib2.install_opener(opener);
    parameters = search_params
    enc_params = urllib.urlencode(parameters)
    request = urllib2.Request('http://www.ebi.ac.uk/Tools/hmmer/search/phmmer',enc_params)
    results_url = urllib2.urlopen(request).getheader('location')
    print "results url %s " %results_url
    enc_res_params = urllib.urlencode(res_params)
    modified_res_url = results_url + '?' + enc_res_params
    results_request = urllib2.Request(modified_res_url)
    data = urllib2.urlopen(results_request)
    download_seq_param = urllib.urlencode(  {'format':'fullfasta'}  )
    jobid = results_url.split('/')[-2]
    print "job id %s" %jobid
    download_url = 'http://www.ebi.ac.uk/Tools/hmmer/download/%s/score' %jobid + '?' + "%s" %download_seq_param
    download_request = urllib2.Request(download_url)
    print "downloading from %s" %download_url
    print "now trying to download the full sequences ..."
    datagz = urllib2.urlopen(download_request, timeout=500)
    with open('%s.gz' %database, 'w' ) as fh:
        fh.write(datagz.read())

    with open(json_file_name,'w') as fh:
        fh.write(data.read())
        print "Got the json file to write"

    if not path.isfile(database):
        output = gzip.open(database+".gz", 'rb')
        outfh = open('%s' %database,'wb')
        outfh.write( output.read() )
        outfh.close()

    json_data=open(json_file_name)
    data = json.load(json_data)
#    print "Number of hits found: %s" %( len(data['results']['hits']) )
#    mylist = []
#    for i in range( 0, int(len( data['results']['hits'] ))  ):
#        name = data['results']['hits'][i]['acc']
#        mylist.append(name)
#
#   json_data.close()

    return data

def get_pid(name):
    mylist = []
    print 'checking for %s' %name
    cmd = ['esl-alipid','combo.msa.fasta.clean']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline,''):
        if line.startswith(name):
            myline = AlipidLine(line)
            print "%s %s" %(myline.name,str(myline.pid))
            mylist.append(myline)

    mytemplatesequences = filter_pid(mylist)
    return mytemplatesequences

def remove_dup_seqs(records):
    checksums = set()
    for record in records:
        checksum = seguid(record.seq)
        if checksum in checksums:
            print "Ignoring %s" % record.id
            continue
        checksums.add(checksum)
        yield record
