# Pseudogene Prediction Using PseudoPipe

This guide outlines step-by-step instructions to predict pseudogenes using **PseudoPipe**, using chimpanzee data as an example.

> **Citation**  
> Zhang Z, Carriero N, Zheng D, Karro J, Harrison PM, Gerstein M. *PseudoPipe: an automated pseudogene identification pipeline*. Bioinformatics. 2006 Jun 15;22(12):1437-9.

---

## Step 0: Requirements

- Unix (tested with bash on Ubuntu)
- Python 2.0
- `blast-2.2.13`
- `fasta-35.1.5`
- PseudoPipe

---

## Step 1: Create Input and Output Directories

```
mkdir ppipe_input
mkdir ppipe_output
```

---

## Step 2: Create Species Subdirectories

```
mkdir ppipe_input/panTro3
mkdir ppipe_output/panTro3
```

---

## Step 3: Download Input Files (DO NOT gunzip)

### Step 3.1: Download DNA Files from Ensembl

```
mkdir dna
```

Download:

```
ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/dna/Pan_troglodytes.Pan_tro_3.0.dna.chromosome.*.fa.gz  
ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/dna/Pan_troglodytes.Pan_tro_3.0.dna_rm.chromosome.*.fa.gz
```

---

### Step 3.2: Download Peptide File

```
mkdir pep
```

Download:

```
ftp://ftp.ensembl.org/pub/release-99/fasta/pan_troglodytes/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa.gz
```

---

### Step 3.3: Download MySQL Files

```
mkdir mysql
```

Download:

```
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/exon_transcript.txt.gz  
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/exon.txt.gz  
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/pan_troglodytes_core_99_3.sql.gz  
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/seq_region.txt.gz  
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/transcript.txt.gz  
ftp://ftp.ensembl.org/pub/release-99/mysql/pan_troglodytes_core_99_3/translation.txt.gz
```

---

## Step 4: Process Downloaded Files

### Step 4.1: Set Up `env.sh`

Save the following as `env.sh` in the same directory as `processEnsemblFiles.sh`:

```
#!/bin/sh

if [ ! -z "$PSEUDOPIPE_ENV" ]; then source $PSEUDOPIPE_ENV; return; fi

export PSEUDOPIPE_HOME=$(cd `dirname $0`/../; pwd)
export pseudopipe=$PSEUDOPIPE_HOME/core/runScripts.py
export genPgeneResult=$PSEUDOPIPE_HOME/ext/genPgeneResult.sh
export genFullAln=$PSEUDOPIPE_HOME/ext/genFullAln.sh
export fastaSplitter=$PSEUDOPIPE_HOME/ext/splitFasta.py
export sqDedicated=$PSEUDOPIPE_HOME/ext/sqDedicated.py
export sqDummy=$PSEUDOPIPE_HOME/ext/sqDummy.py
export blastHandler=$PSEUDOPIPE_HOME/core/processBlastOutput.py
export extractExLoc=$PSEUDOPIPE_HOME/core/extractKPExonLocations-Aug2016.py

export pythonExec=/bin/python2

export formatDB=pathTo/blast-2.2.13/bin/formatdb
export blastExec=pathTo/blast-2.2.13/bin/blastall
export fastaExec=pathTo/fasta-35.1.5/tfasty35
```

### Step 4.2: Run Preprocessing Script

```
cd ppipe_input/panTro3/
pathTo/PseudoPipe/bin/processEnsemblFiles.sh ./
```

### Step 4.3: Verify DNA Database Files

Ensure these files exist in `dna/`:

```
dna_rm.fa  
dna_rm.fa.nhr  
dna_rm.fa.nin  
dna_rm.fa.nsd  
dna_rm.fa.nsi  
dna_rm.fa.nsq
```

If not, run:

```
formatdb -i dna_rm.fa -o T -p F
```

---

## Step 5: Create Output Directories and BLAST Jobs

```
pathTo/PseudoPipe/ext/ppipe.sh \\
pathTo/ppipe_output/panTro3 \\
pathTo/ppipe_input/panTro3/dna/dna_rm.fa \\
pathTo/ppipe_input/panTro3/dna/Pan_troglodytes.Pan_tro_3.0.dna.chromosome.%s.fa \\
pathTo/ppipe_input/panTro3/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa \\
pathTo/ppipe_input/panTro3/mysql/chr%s_exLocs \\
0
```

---

## Step 6: Submit BLAST Jobs

> **Note:** This step is compute-intensive and takes time.

---

## Step 7: Process the BLAST Output

### Step 7.1: Create Job List

```
cd pathTo/ppipe_output/panTro3/blast/processed/

echo "cd $(pwd); pathTo/PseudoPipe/core/processBlastOutput.py pathTo/ppipe_input/panTro3/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa 'split\\\\d{4}.Out\\\\Z' pathTo/output ; touch processed.stamp" > jobs
```

---

## Step 8: Results on the Minus
