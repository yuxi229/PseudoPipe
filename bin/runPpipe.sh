#/bin/sh
if [ $# -lt 4 ]
then
        echo "Usage: $0 [output dir] [config file] [nodes] [queue]"
        exit 1
fi

if [ ! -e $2 ]
then
	echo "Error: the configuration file does not exist"	
	exit 1
fi

run=`dirname $0`/run.sh

confFile=$2

dnaDir=`grep 'dna:' $confFile | sed 's/.*:\(.*\)/\1/'`
mskDir=`grep 'masked:' $confFile | sed 's/.*:\(.*\)/\1/'`
exnDir=`grep 'exons:' $confFile | sed 's/.*:\(.*\)/\1/'`
pepDir=`grep 'pep:' $confFile | sed 's/.*:\(.*\)/\1/'`

$run "$1" "$mskDir" "$dnaDir" "$pepDir" "$exnDir" "$3" $4
