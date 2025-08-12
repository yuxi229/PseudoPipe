# PseudoPipe – Conda Installation and Usage

When you predict pseudogenes using PseudoPipe first time, we suggest you to run PseudoPipe step by step.

Here shows an example of using PseudoPipe to predict pseudogenes in chimpanzee.

To cite Pseudopipe, please refer to the following publication:

Zhang Z, Carriero N, Zheng D, Karro J, Harrison PM, Gerstein M. PseudoPipe: an automated pseudogene identification pipeline. Bioinformatics. 2006 Jun 15;22(12):1437-9.

---

## Step 0. Requirements

- Unix-like OS (tested on Ubuntu, bash shell)  
- Python ≥ 3.1 (installed via Conda)  
- BLAST+ 2.16.0 (installed via Conda)  
- FASTA 35.1.5 (specifically `tfasty35` — **not included in Conda**, install manually from [FASTA download page](https://fasta.bioch.virginia.edu/wrpearson/fasta/fasta33-35/))  
- PseudoPipe (installed via Conda package)  

---

## Step 1. Install PseudoPipe via Conda

### Option A: Install from your Conda channel

```bash
conda install -c <your-channel> pseudopipe
```


### Option B: Build and install locally for testing
```bash
conda build recipe
conda install --use-local pseudopipe
```

Optional: Create and activate environment from environment.yml

```bash
conda env create -f environment.yml
conda activate pseudopipe-env
```

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

## Step 3. Download ENSEMBL Data
### Option A: Use built-in downloader CLI (recommended)

```bash
cd ppipe_input
pseudopipe-downloadFiles ./
```
1. Follow prompts to select Ensembl release (leave blank for latest).
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

## Step 4. Process ENSEMBL Files
Activate your Conda environment if not already active:

```bash
conda activate pseudopipe-env
```
Process files to format genome database for BLAST:

```bash
cd ppipe_input/panTro3
pseudopipe-processEnsemblFiles ./
```

Check that masked DNA database files exist (dna_rm.fa, .nhr, .nin, .nsq, etc.).
If missing, create BLAST database manually:

```bash
makeblastdb -in dna_rm.fa -dbtype nucl -out dna_rm
```

## Step 5. Create Output Directories and Generate BLAST Jobs
Run the main pipeline script:

```bash
pseudopipe-ppipe \
  ppipe_output/panTro3 \
  ppipe_input/panTro3/dna/dna_rm.fa \
  ppipe_input/panTro3/dna/Pan_troglodytes.Pan_tro_3.0.dna.chromosome.*.fa \
  ppipe_input/panTro3/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa \
  ppipe_input/panTro3/mysql/chr*_exLocs \
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

## Step 6. Submit and Run BLAST Jobs
Submit the jobs generated in blast/jobs (using your HPC scheduler).

Wait for completion; .out files will appear in blast/output/.

## Step 7. Process BLAST Output

```bash
cd ppipe_output/panTro3/blast/processed
```

Create job list to process BLAST results:

bash
echo "cd $(pwd); pseudopipe-processBlastOutputs \
  ppipe_input/panTro3/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa \
  'split\\d{4}.Out\\Z' \
  ppipe_output ; touch processed.stamp" > jobs
```

Submit jobs using your scheduler.

## Step 8. Run PseudoPipe on Minus Strand
Set pipeline environment variables in setenvPipelineVars.sh:

```bash
dataDir=ppipe_output/panTro3

export BlastoutSortedTemplate=${dataDir}/blast/processed/%s_M_blastHits.sorted
export ChromosomeFastaTemplate=ppipe_input/panTro3/dna/Pan_troglodytes.Pan_tro_3.0.dna.chromosome.%s.fa
export ExonMaskTemplate=ppipe_input/panTro3/mysql/chr%s_exLocs
export ExonMaskFields='2 3'
export FastaProgram=path/to/tfasty35     # Install FASTA suite manually
export ProteinQueryFile=ppipe_input/panTro3/pep/Pan_troglodytes.Pan_tro_3.0.pep.all.fa
```

Create jobs:

```bash
cd ppipe_output/panTro3/pgenes/minus

ms=$(cd ../../blast/processed; for f in *_M_*sorted; do echo ${f/_M_blastHits.sorted/}; done)

for c in $ms; do
  echo "cd $(pwd); source ./setenvPipelineVars.sh; touch stamp/$c.Start; pseudopipe-runScripts $c > log/$c.log 2>&1; touch stamp/$c.Stop"
done > jobs
```

Submit jobs.

## Step 9. Run PseudoPipe on Plus Strand
Set setenvPipelineVars.sh with plus strand BLAST files:

```bash
export BlastoutSortedTemplate=${dataDir}/blast/processed/%s_P_blastHits.sorted
```

Create and submit jobs similarly:

```bash
cd ppipe_output/panTro3/pgenes/plus

ms=$(cd ../../blast/processed; for f in *_P_*sorted; do echo ${f/_P_blastHits.sorted/}; done)

for c in $ms; do
  echo "cd $(pwd); source ./setenvPipelineVars.sh; touch stamp/$c.Start; pseudopipe-runScripts $c > log/$c.log 2>&1; touch stamp/$c.Stop"
done > jobs
```

Submit jobs.

## Step 10. Generate Final Results
Generate pseudogene annotation file:

```bash
pseudopipe-genPgeneResult ppipe_output/panTro3 Pan_troglodytes.Pan_tro_3.0.pgene.txt
Generate pseudogene alignment file:
```

```bash
pseudopipe-genFullAln ppipe_output/panTro3 Pan_troglodytes.Pan_tro_3.0.pgene.align.gz
```

Generate exon annotation file:

```bash
pseudopipe-genPgeneResultExon ppipe_output/panTro3 Pan_troglodytes.Pan_tro_3.0.pexon.txt
```

Notes
TFASTY from the FASTA suite is not included in the Conda package due to licensing.
Install manually from FASTA download page and update setenvPipelineVars.sh accordingly.

All pseudopipe-* CLI commands become available after activating the Conda environment.

Replace path/to/ placeholders with actual paths on your system.

Job submission depends on your HPC scheduler (e.g., qsub, sbatch, bsub).
