# PseudoPipe – Conda Installation and Usage

When you predict pseudogenes using PseudoPipe first time, we suggest you to run PseudoPipe step by step.

Here shows an example of using PseudoPipe to predict pseudogenes in chimpanzee.

To cite Pseudopipe, please refer to the following publication:

> **Citation**  
> Zhang Z, Carriero N, Zheng D, Karro J, Harrison PM, Gerstein M. *PseudoPipe: an automated pseudogene identification pipeline*. Bioinformatics. 2006 Jun 15;22(12):1437-9.

For more information visit http://www.pseudogene.org/pseudopipe/ 

For instructions on installation and usage **without conda** please view ... 

---

## Step 0. Requirements

- Unix-like OS (tested on Ubuntu, bash shell)  
- Python ≥ 3.1 (installed via Conda)  
- BLAST+ 2.16.0 (installed via Conda)  
- FASTA 35.1.5 (specifically `tfasty35` — **not included in Conda**, install manually from [FASTA download page](https://fasta.bioch.virginia.edu/wrpearson/fasta/fasta33-35/))  
- PseudoPipe (installed via Conda package)  

---

## Step 1. Install PseudoPipe via Conda

### Option A: Install from Conda channel (recommended)

You can install **PseudoPipe** directly via Conda from the `yuxizhang` channel (recommended):

```bash
conda install -c yuxi229 pseudopipe
```

```bash
conda install -c bioconda blast=2.16.0
```

### Option B: Build from source using conda-build

Install conda-build if not already installed
```bash
conda install conda-build
```

Clone your repo

```bash
git clone https://github.com/yuxi229/PseudoPipe.git
cd PseudoPipe
```

Build the package locally
```bash
conda build recipe/
```
Install the built package into a new environment

```bash
conda create -n pseudopipe-env python=3.11
conda activate pseudopipe-env
conda install --use-local pseudopipe
```

---

## Step 2. Prepare Working Directories

 Create an input and output directories
```bash
mkdir ppipe_input
mkdir ppipe_output
```

Create a species directory in the input and output
```bash
mkdir ppipe_input/panTro3
mkdir ppipe_output/panTro3
```
---

## Step 3. Download ENSEMBL Data
### Option A: Use built-in downloader CLI (recommended)

```bash
cd ppipe_input/panTro3
downloadFiles.sh
```
1. Follow prompts to select Ensembl release (leave blank for latest). TYPE 114 FOR NOW, IT THINKS 115 IS LATEST RELEASE BUT ITS NOT
2. Choose species (e.g., pan_troglodytes).

Files will download into the respective species directory.

### Option B: Manual download (for species not listed)

```bash
cd ppipe_input/panTro3
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
Activate your Conda environment if not already active:

```bash
conda activate pseudopipe-env
```
Permanently export the path to your input and output directories
```bash
# Add to your ~/.bashrc or ~/.bash_profile
echo 'export INPUT_DIR="pathTo/ppipe_input/panTro3"' >> ~/.bashrc
echo 'export OUTPUT_DIR="pathTo/conda_new/ppipe_output/panTro3"' >> ~/.bashrc

# Reload your bashrc
source ~/.bashrc

```

Process files to format genome database for BLAST:

```bash
cd ppipe_input/panTro3
processEnsemblFiles.sh ./
```

Check that masked DNA database files exist (dna_rm.fa, .nhr, .nin, .nsq, etc.).
If missing, create BLAST database manually:

```bash
makeblastdb -in dna_rm.fa -dbtype nucl -out dna_rm
```
CHECK THIS ^
---

## Step 5. Create Output Directories and Generate BLAST Jobs
Run the main pipeline script:

```bash
pseudopipe-ppipe \
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
