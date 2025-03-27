#/bin/sh
if [ $# -lt 6 ]
then
        echo "Usage: $0 [output dir] [masked dna file/dir] [dna files pattern/dir] [pep file/dir] [exon files pattern/dir] [nodes] [queue (optional)]"
        exit 1
fi

extdir=`dirname $0`/../ext

if [ "$6" != "0" ]
then
	$extdir/sqPBS.py "$1" "$2" "$3" "$4" "$5" "$6" $7 | qsub > Queued
else
	$extdir/pseudopipe.sh "$1" "$2" "$3" "$4" "$5" 0
fi
