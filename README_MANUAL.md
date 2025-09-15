# PseudoPipe – Conda Installation and Usage

When you predict pseudogenes using PseudoPipe first time, we suggest you to run PseudoPipe step by step.

Here shows an example of using PseudoPipe to predict pseudogenes in humans.

To cite Pseudopipe, please refer to the following publication:

> **Citation**  
> Zhang Z, Carriero N, Zheng D, Karro J, Harrison PM, Gerstein M. *PseudoPipe: an automated pseudogene identification pipeline*. Bioinformatics. 2006 Jun 15;22(12):1437-9.

For more information visit http://www.pseudogene.org/pseudopipe/ and https://www.gersteinlab.org/

For instructions on installation and usage **without conda** please view ... 

---

## Step 0. Requirements

- Unix-like OS (tested on Ubuntu, bash shell)  
- Python ≥ 3.1 (installed via Conda)  
- BLAST+ 2.16.0 (installed via Conda)  
- FASTA 35.1.5 (specifically `tfasty35` — **not included in Conda**, install manually from [FASTA download page](https://fasta.bioch.virginia.edu/wrpearson/fasta/fasta33-35/))  
- PseudoPipe (installed via Conda package)  

---

## Step 1. Clone the repo 

---

## Step 2. Prepare Working Directories

 Create an input and output directories and a species directory in the input and output
```bash
mkdir ppipe_input
mkdir ppipe_output
mkdir ppipe_input/human
mkdir ppipe_output/human

```

---

## Step 3. Download ENSEMBL Data
### Option A: Use built-in downloader CLI (recommended)

```bash
cd ppipe_input/human
pathTo/PseudoPipe/bin/downloadFiles.sh ./ 
```
1. Follow prompts to select species (exact, official species name is required) 
2. Follow prompts to select release 

Files will download into the respective species directory.

### Option B: Manual download 

```bash
cd ppipe_input/human
mkdir dna pep mysql
```

Download DNA files into the dna directory (do not decompress .gz):

```bash
wget ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/dna/Pan_troglodytes.Pan_tro_3.0.dna.chromosome.*.fa.gz -P dna/
wget ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/dna/Pan_troglodytes.Pan_tro_3.0.dna_rm.chromosome.*.fa.gz -P dna/
```

Download peptide file into the pep directory:

```bash
wget ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa.gz -P pep/
```

Download MySQL annotation files into the mysql directory: 

```bash
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/exon_transcript.txt.gz 
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/exon.txt.gz
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/pan_troglodytes_core_99_3.sql.gz
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/seq_region.txt.gz
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/transcript.txt.gz
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/translation.txt.gz
```

---

## Step 4. Process ENSEMBL Files
Set the env.sh and put in the same dir as processEnsemblFiles.sh
It should be in pathTo/PseudoPipe/bin/env.sh 

```bash
cd pathTo/PseudoPipe/bin
nano env.sh 
```

```bash
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
export extractExLoc=$PSEUDOPIPE_HOME/core/extractKPExonLocations-Aug2016.py

# Python configuration
export pythonExec=/bin/python3

# Alignment tools configuration
export makeblastdb=pathTo/blast-2.2.13/bin/formatdb
export blastExec=pathTo/blast-2.2.13/bin/blastall
export fastaExec=pathTo/fasta-35.1.5/tfasty35

```

Process files to format genome database for BLAST:

```bash
cd $INPUT_DIR
pathTo/PseudoPipe/bin/processEnsemblFiles.sh ./
```

Check that masked DNA database files exist (dna_rm.fa, .nhr, .nin, .nsq, etc.).
If missing, create BLAST database manually:

```bash
makeblastdb -in dna_rm.fa -dbtype nucl -out dna_rm \
    -parse_seqids -blastdb_version 5
```
---

## Step 5. Create Output Directories and Generate BLAST Jobs
Run the main pipeline script:

```bash
pathTo/PseudoPipe/ext/ppipe.sh \
    "$OUTPUT_DIR" \
    "$INPUT_DIR/dna/dna_rm.fa" \
    "$INPUT_DIR/dna/Homo_sapiens.GRCh38.dna_rm.chromosome.*.fa" \
    "$INPUT_DIR/pep/Homo_sapiens.GRCh38.pep.all.fa" \
    "$INPUT_DIR/mysql/chr*_exLocs" \
    0
```

Check that the following directories are created inside ppipe_output/panTro3:

blast
dna
pep
pgenes

Inside blast/, confirm files like:

split peptide files named split*
jobs
directories: output/, processed/, stamps/, status/

---

## Step 6. Submit and Run BLAST Jobs
Submit the jobs generated in blast/jobs (using your HPC scheduler).

Wait for completion; .out files will appear in blast/output/.

---

## Step 7. Process BLAST Output

```bash
cd "$OUTPUT_DIR/blast/processed"
```

Create job list to process BLAST results:

```bash
echo "cd $(pwd); pseudopipe-processBlastOutputs \
    "$INPUT_DIR/pep/Homo_sapiens.GRCh38.pep.all.fa" \
    'split\d{4}.Out\Z' \
    ../output; touch processed.stamp" > jobs
```

Submit jobs using your scheduler.
There should be files in the processed directory. 

---

## Step 8. Run PseudoPipe on Minus Strand
Create and source the environment file setenvPipelineVars.sh:

```bash
cd "$OUTPUT_DIR/pgenes/minus"
```

```bash
cat > setenvPipelineVars.sh << EOF
#!/bin/bash
export dataDir="$OUTPUT_DIR"
export BlastoutSortedTemplate="$OUTPUT_DIR/blast/processed/%s_M_blastHits.sorted"
export ChromosomeFastaTemplate="$INPUT_DIR/dna/Homo_sapiens.GRCh38.dna.chromosome.%s.fa"
export ExonMaskTemplate="$INPUT_DIR/mysql/chr%s_exLocs"
export ExonMaskFields='2 3'
export FastaProgram="/gpfs/gibbs/pi/gerstein/yz2478/conda_new/PseudoPipe/dependencies/fasta-35.1.5/tfasty35"
export ProteinQueryFile="$INPUT_DIR/pep/Homo_sapiens.GRCh38.pep.all.fa"
EOF

source setenvPipelineVars.sh
```

Create jobs:

```bash
ms=$(cd ../../blast/processed; for f in *_M_*sorted; do echo ${f/_M_blastHits.sorted/}; done)

for c in $ms; do
  echo "cd $(pwd); source ./setenvPipelineVars.sh; touch stamp/$c.Start; pseudopipe-runScripts $c > log/$c.log 2>&1; touch stamp/$c.Stop"
done > jobs
```

Submit jobs.

You should see pgenes, pexons, polya directories on success. (Check log if errors occur) 

---

## Step 9. Run PseudoPipe on Plus Strand
Create and source the environment file setenvPipelineVars.sh:

```bash
cd "$OUTPUT_DIR/pgenes/plus"
```

```bash
cat > setenvPipelineVars.sh << EOF
#!/bin/bash
export dataDir="$OUTPUT_DIR"
export BlastoutSortedTemplate="$OUTPUT_DIR/blast/processed/%s_P_blastHits.sorted"
export ChromosomeFastaTemplate="$INPUT_DIR/dna/Homo_sapiens.GRCh38.dna.chromosome.%s.fa"
export ExonMaskTemplate="$INPUT_DIR/mysql/chr%s_exLocs"
export ExonMaskFields='2 3'
export FastaProgram="/gpfs/gibbs/pi/gerstein/yz2478/conda_new/PseudoPipe/dependencies/fasta-35.1.5/tfasty35"
export ProteinQueryFile="$INPUT_DIR/pep/Homo_sapiens.GRCh38.pep.all.fa"
EOF

source setenvPipelineVars.sh
```

Create jobs:

```bash
ms=$(cd ../../blast/processed; for f in *_P_*sorted; do echo ${f/_P_blastHits.sorted/}; done)

for c in $ms; do
  echo "cd $(pwd); source ./setenvPipelineVars.sh; touch stamp/$c.Start; pseudopipe-runScripts $c > log/$c.log 2>&1; touch stamp/$c.Stop"
done > jobs
```

Submit jobs.

---

## Step 10. Generate Final Results
Generate pseudogene annotation file:

```bash
pseudopipe-genPgeneResult $OUTPUT_DIR Homo_sapiens.Homo_sapiens_3.0.pgene.txt
Generate pseudogene alignment file:
```

```bash
pseudopipe-genFullAln $OUTPUT_DIR Homo_sapiens.Homo_sapiens_3.0.pgene.align.gz
```

Generate exon annotation file:

```bash
pseudopipe-genPgeneResultExon $OUTPUT_DIR Homo_sapiens.Homo_sapiens_3.0.pexon.txt
```
---

Notes
TFASTY from the FASTA suite is not included in the Conda package due to licensing.
Install manually from FASTA download page and update setenvPipelineVars.sh accordingly.

All pseudopipe-* CLI commands become available after activating the Conda environment.

Replace path/to/ placeholders with actual paths on your system.

Job submission depends on your HPC scheduler (e.g., qsub, sbatch, bsub).
