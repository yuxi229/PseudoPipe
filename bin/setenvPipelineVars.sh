#!/bin/bash

dataDir=/gpfs/gibbs/pi/gerstein/yz2478/ppipe_output/human/

export BlastoutSortedTemplate=${dataDir}/blast/processed/%s_M_blastHits.sorted
export ChromosomeFastaTemplate=/gpfs/gibbs/pi/gerstein/yz2478/ppipe_input/human/dna/Homo_sapiens.GRCh38.dna.chromosome.%s.fa
export ExonMaskTemplate=/gpfs/gibbs/pi/gerstein/yz2478/ppipe_input/human/mysql/chr%s_exLocs
export ExonMaskFields='2 3'
export FastaProgram=/gpfs/gibbs/pi/gerstein/yz2478/PseudoPipe/dependencies/fasta-36.3.8i/bin/tfasty36
export ProteinQueryFile=/gpfs/gibbs/pi/gerstein/yz2478/ppipe_input/human/pep/Homo_sapiens.GRCh38.pep.all.fa
