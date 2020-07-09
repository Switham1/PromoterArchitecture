from Bio.SeqUtils import GC
from Bio import SeqIO
import os
import argparse

parser = argparse.ArgumentParser(description='promoter_GC_content')
parser.add_argument('file_names', type=str, help='Name of folder and filenames for the promoters extracted')
parser.add_argument('promoters_fasta', type=str, help='Input location of promoter fasta')
parser.add_argument('GC_content_tsv', type=str, help='Output location of promoters GC_content tsv file')
args = parser.parse_args()

def GC_content(dna_fasta, output_file):
    """function to calculate GC content % of sequences in a fast file and output a text file"""

    fasta_sequences = SeqIO.parse(open(dna_fasta),'fasta')
    with open(output_file, 'w') as fout:

        for fasta in fasta_sequences:
                name, sequence = fasta.id, str(fasta.seq)

                fout.write(f'{name}\t{GC(sequence)}\n')
                
                


#make directory for the output file to be exported to
dirName = f'../../data/output/{args.file_names}/GC_content'
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory " , dirName ,  " created") 
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

GC_content(args.promoters_fasta, args.GC_content_tsv)