#/bin/sh!
if [ $# -lt 1 ]
then
	echo $0 [target dir]
	exit 0
fi

if [ ! -d $1 ]
then
	echo Target dir \'$1\' not exists
	exit 1
fi

cd $1

. `dirname $0`/env.sh

cd dna
echo Uncompressing DNAs
for f in *dna_rm*.fa.gz; do gunzip -c $f; done > dna_rm.fa
for f in *dna.chr*.fa.gz; do gunzip $f; done
echo Formatting Repeat Masked DNAs
$formatDB -i dna_rm.fa -o T -p F
cd ..

cd pep
echo Uncompressing Peptides
gunzip *.pep.all.fa.gz
cd ..

cd mysql
echo Uncompressing Exons
for i in `find . -name '*.gz'`; do gunzip $i; done
cut translation.txt -f1,7-10 > translation_stable_id.txt
echo Extracting Exons
$extractExLoc ../pep/*.pep.all.fa
cd ..

echo Generating Job Configuration File
targetDir=`pwd`
jobConf=$targetDir/`basename $targetDir`.conf
cfilePrefix=`cd dna; ls *.dna_rm.chromosome.* | head -n 1 | sed 's/\(.*\)\.dna_rm\.chromosome\..*/\1/'`
echo masked:$targetDir/dna/dna_rm.fa > $jobConf
echo dna:$targetDir/dna/$cfilePrefix.dna.chromosome.%s.fa >> $jobConf
echo exons:$targetDir/mysql/chr%s_exLocs >> $jobConf
echo pep:$targetDir/pep/$cfilePrefix.pep.all.fa >> $jobConf
