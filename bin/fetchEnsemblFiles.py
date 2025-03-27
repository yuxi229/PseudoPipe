#!/usr/bin/env python

# some examples of files and locations
# pub
# lrwxrwxrwx   1 ftpuser  ftpusers        30 Dec  7 16:33 current_homo_sapiens -> release-36/homo_sapiens_36_35i
#
#/pub/release-36/homo_sapiens_36_35i/data/fasta/dna
#-rw-rw-r--   1 ftpuser  ftpusers  67675771 Nov 15 14:48 Homo_sapiens.NCBI35.dec.dna.chromosome.1.fa.gz
#-rw-rw-r--   1 ftpuser  ftpusers  40802343 Nov 15 14:55 Homo_sapiens.NCBI35.dec.dna_rm.chromosome.1.fa.gz
#
#/pub/release-36/homo_sapiens_36_35i/data/fasta/pep
#-rw-rw-r--   1 ftpuser  ftpusers   3817861 Nov 15 19:46 Homo_sapiens.NCBI35.dec.pep.known.fa.gz
#
#/pub/release-36/homo_sapiens_36_35i/data/mysql/homo_sapiens_core_36_35i
#-rw-rw-r--   1 ftpuser  ftpusers   2957452 Dec  2 22:45 exon.txt.table.gz
#-rw-rw-r--   1 ftpuser  ftpusers   1747738 Dec  2 22:45 exon_stable_id.txt.table.gz
#-rw-rw-r--   1 ftpuser  ftpusers   1489045 Dec  2 22:45 exon_transcript.txt.table.gz
#-rw-rw-r--   1 ftpuser  ftpusers      4626 Dec  2 21:57 homo_sapiens_core_36_35i.mysql40_compatible.sql.gz
#-rw-rw-r--   1 ftpuser  ftpusers      4753 Dec  2 21:57 homo_sapiens_core_36_35i.sql.gz

import os, os.path, re, sys
from ftplib import FTP

class collect:
    def __init__(self): self.data = []
    def more(self, l): self.data.append(l)

def maybeRetrFile(fromPath, toPath):
    what = 'from %s --> to %s' %(fromPath, toPath)
    if os.path.exists(toPath):
        print 'skipping '+what
        return
    else:
        if toPath.endswith('.gz') and os.path.exists(toPath[:-3]):
            print 'skipping (uncompressed) '+what
            return
            
    print what
    toFile = open(toPath, 'w')
    ec.retrbinary('RETR '+fromPath, toFile.write, blocksize=100000)
    toFile.close()

target = sys.argv[1].strip().lower().replace(' ', '_')

release = 'current_'

if len(sys.argv) > 2:
	release = 'release-' + sys.argv[2] + '/'

# set up initial connection
host='ftp.ensembl.org'
print 'Logging into '+host
ec = FTP(host)
ec.login()

# look for target in a listing of pub
files = collect()
where='pub/'+release+'mysql'
print 'Listing '+where
ec.dir(where, files.more)
tEntries = [l for l in files.data if target+"_core_" in l and '->' not in l ]
if len(tEntries) != 1:
    print target + ' is either missing or not unique:'
    print tEntries
    print '\n'.join(files.data)
    ec.close()
    sys.exit(-1)

# "parse" current link name
curPat = re.compile(r''+target+'_core_(.+)_(.+)\Z')
tPath = tEntries[0].split()[-1]
mo = curPat.match(tPath)
if not mo:
    print 'dont\'t understand release naming scheme: '+ tPath
    ec.close()
    sys.exit(-1)
[maj, min] = mo.groups()
majMin=maj+'_'+min
outDir = target + '_' + majMin
    
print 'Release: '+release[0:len(release)-1]+', '+'tPath: '+tPath+', '+'target: '+target+', '+'maj: '+maj+', '+'majMin: '+majMin+', '+'outDir: '+outDir

## if os.path.exists(outDir):
##     print 'up to date: ' + tPath
##     ec.close()
##     sys.exit(0)

# need to get files. first, set up directories.
[dDir, mDir, pDir] = [outDir+d for d in ['/dna/', '/mysql/', '/pep/']]
if not os.path.exists(dDir): os.makedirs(dDir, 0744)
if not os.path.exists(mDir): os.makedirs(mDir, 0744)
if not os.path.exists(pDir): os.makedirs(pDir, 0744)

# retrieve dna
dnaPat = re.compile(r'\.dna(_rm)?\.chromosome\..+\.fa\.gz\Z')
dFiles = collect()
where = 'pub/'+release+'fasta/%s/dna' % target
print 'Changing dir to '+where
ec.dir(where, dFiles.more)
dKeep = [l for l in dFiles.data if dnaPat.search(l)]
for f in dKeep:
    fn = f.split()[-1]
    maybeRetrFile(where+'/'+fn, dDir+fn)

# retrieve pep
where = 'pub/'+release+'fasta/%s/pep' % target
pFiles = collect()
print 'Changing dir to '+where
ec.dir(where, pFiles.more)
for f in pFiles.data:
    fn = f.split()[-1]
    maybeRetrFile(where+'/'+fn, pDir+fn)

# retrieve mysql
# older releases?: mFiles = ['exon.txt.table', 'exon_transcript.txt.table', 'gene_stable_id.txt.table', 'seq_region.txt.table', 'transcript.txt.table', 'translation.txt.table', 'translation_stable_id.txt.table', target+'_core_'+majMin+'.sql', target+'_core_'+majMin+'.mysql40_compatible.sql']
#older releases which have *_stable_id.txt: mFiles = ['exon.txt', 'exon_transcript.txt', 'gene_stable_id.txt', 'seq_region.txt', 'transcript.txt', 'translation.txt', 'translation_stable_id.txt', target+'_core_'+majMin+'.sql']
mFiles = ['exon.txt', 'exon_transcript.txt', 'seq_region.txt', 'transcript.txt', 'translation.txt', target+'_core_'+majMin+'.sql']

where = 'pub/'+release+'mysql/%s_core_%s' % (target, majMin)
print 'Changing dir to '+where
for mf in mFiles:
    maybeRetrFile(where+'/'+mf+'.gz', mDir+mf+'.gz')

# retrieve GTF
where = 'pub/'+release+'gtf/%s' % (target)
print 'Changing dir to '+where
gtfPat = re.compile(r'\.gtf\.gz\Z')
gFiles = collect()
ec.dir(where, gFiles.more)
gKeep = [l for l in gFiles.data if gtfPat.search(l)]
for f in gKeep:
    fn = f.split()[-1]
    maybeRetrFile(where+'/'+fn, mDir+fn)

ec.close()

print 'Processing Fetched Files'
#os.system('%s/processEnsemblFiles.sh %s' % (sys.path[0], outDir))
