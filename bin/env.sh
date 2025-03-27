#!/bin/sh

if [ ! -z "$PSEUDOPIPE_ENV" ]; then source $PSEUDOPIPE_ENV; return; fi

# Pseudopipe configuration
export PSEUDOPIPE_HOME=`cd \`dirname $0\`/../; pwd`
export pseudopipe=$PSEUDOPIPE_HOME/core/runScripts.py
export genPgeneResult=$PSEUDOPIPE_HOME/ext/genPgeneResult.sh
export genFullAln=$PSEUDOPIPE_HOME/ext/genFullAln.sh
export fastaSplitter=$PSEUDOPIPE_HOME/ext/splitFasta.py
export sqDedicated=$PSEUDOPIPE_HOME/ext/sqDedicated.py
export sqDummy=$PSEUDOPIPE_HOME/ext/sqDummy.py
export blastHandler=$PSEUDOPIPE_HOME/core/processBlastOutput.py
export extractExLoc=$PSEUDOPIPE_HOME/core/extractKPExonLocations-Aug2016.py # extractKPExonLocations-Jan2016.py

# Python configuration
export pythonExec=python


# Alignment tools configuration
export formatDB=/gpfs/gibbs/pi/gerstein/yz2478/PseudoPipe/dependencies/blast-2.2.13/bin/formatdb
export blastExec=/gpfs/gibbs/pi/gerstein/yz2478/PseudoPipe/dependencies/blast-2.2.13/bin/blastall
export fastaExec=/gpfs/gibbs/pi/gerstein/yz2478/PseudoPipe/dependencies/fasta-36.3.8i/bin/tfasty36



