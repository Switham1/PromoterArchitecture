import argparse
import io
import os

import pandas as pd
from pybedtools import BedTool


def parse_args(args):
    """define arguments"""
    parser = argparse.ArgumentParser(description="TATA_enrichment")
    parser.add_argument(
        "file_names",
        type=str,
        help="Name of folder and filenames for the promoters extracted",
    )
    parser.add_argument("promoterpref", type=str, help="Promoter prefix name")
    parser.add_argument(
        "gene_categories",
        type=str,
        help="Input location of the gene categories text file",
    )
    parser.add_argument(
        "promoter_bed_file",
        type=str,
        help="Input location of the promoters bed file",
    )
    parser.add_argument(
        "output_genecat_prefix",
        type=str,
        help="Gene category prefix (eg. Czechowski)",
    )
    parser.add_argument(
        "TATA_box_locations",
        type=str,
        help="Input location of TATAbox_location bed file (from Eukaryotic promoter database)",
    )
    # optional argument
    parser.add_argument("variable1_name", nargs="?", default="constitutive")
    parser.add_argument("variable2_name", nargs="?", default="variable")
    return parser.parse_args(
        args
    )  # let argparse grab args from sys.argv itself to allow for testing in module import


def sort_data(promoter_bed_file, gene_categories):
    """sort the promoters and genes types data ready for gat TATA enrichment"""
    promoters = pd.read_table(promoter_bed_file, sep="\t", header=None)
    col = [
        "chr",
        "start",
        "stop",
        "AGI",
        "dot1",
        "strand",
        "source",
        "type",
        "dot2",
        "attributes",
    ]
    promoters.columns = col
    # read in gene categories
    gene_cats = pd.read_table(gene_categories, sep="\t", header=None)
    cols = ["AGI", "gene_type"]
    gene_cats.columns = cols
    # merge with promoters
    promoters = pd.merge(promoters, gene_cats, on="AGI", how="left")
    # EPD downloaded file motifs (all genes)
    core_motifs_file = "../../data/EPD_promoter_analysis/EPDnew_promoters/db/promoter_motifs.txt"

    # Read in that file
    core_motifs = pd.read_table(core_motifs_file, sep="\t", header=0)
    cols = [
        "AGI",
        "TATA_present",
        "Inr_present",
        "CCAAT_box_present",
        "GC_box_present",
    ]
    core_motifs.columns = cols
    # remove last 2 characters of AGI in cor_motifs df
    core_motifs["AGI"] = core_motifs.AGI.str.slice(0, -2)
    # Merge them with extracted promoters
    merged = pd.merge(promoters, core_motifs, how="left", on="AGI")
    return merged


def prepare_gat(
    df,
    promoter_TATA_intersect_bed,
    TATA_box_locations,
    file_names,
    output_genecat_prefix,
    promoterpref,
    variable1_name,
    variable2_name,
):
    """prepare files for running gat analysis - outputs a workspace file containing all promoters, a variable promoter file and a constitutive promoter file"""
    # make buffer to save promoters
    buffer = io.StringIO()
    df.to_csv(buffer, sep="\t", header=None, index=False)
    buffer.seek(0)
    # select only constitutive and variable genes
    df = df[
        (df.gene_type == variable1_name) | (df.gene_type == variable2_name)
    ]
    # reorder columns
    df_reordered = df[
        [
            "chr",
            "start",
            "stop",
            "gene_type",
            "strand",
            "source",
            "attributes",
            "AGI",
        ]
    ]
    # sort by chromosome and start
    sorted_motifs = df_reordered.sort_values(["chr", "start"])
    # save bed file
    BedTool.from_dataframe(sorted_motifs).saveas(
        f"../../data/output/{file_names}/TATA/{output_genecat_prefix}_{promoterpref}_nocontrol.bed"
    )

    # run bedtools intersect between TATAbox_location_renamed.bed and the extracted promoters
    TATAlocations = BedTool(TATA_box_locations)
    promoters = BedTool(buffer)
    promoters.intersect(
        TATAlocations, wao=True, output=promoter_TATA_intersect_bed
    )
    # make a new gat workspace file with all promoters (first 3 columns)
    BedTool.from_dataframe(sorted_motifs[["chr", "start", "stop"]]).saveas(
        f"../../data/output/{file_names}/TATA/gat_analysis/{output_genecat_prefix}_{promoterpref}_workspace.bed"
    )
    # select only variable promoters
    variable_promoters_extended = sorted_motifs[
        sorted_motifs["gene_type"] == variable2_name
    ]
    sorted_variable = variable_promoters_extended.sort_values(["chr", "start"])
    BedTool.from_dataframe(sorted_variable).saveas(
        f"../../data/output/{file_names}/TATA/gat_analysis/{output_genecat_prefix}_{promoterpref}_{variable2_name}.bed"
    )
    # make a constitutive only file
    constitutive_promoters = sorted_motifs[
        sorted_motifs["gene_type"] == variable1_name
    ]
    sorted_constitutive = constitutive_promoters.sort_values(["chr", "start"])
    BedTool.from_dataframe(sorted_constitutive).saveas(
        f"../../data/output/{file_names}/TATA/gat_analysis/{output_genecat_prefix}_{promoterpref}_{variable1_name}.bed"
    )


def main(args):
    # parse arguments
    args = parse_args(args)

    promoter_TATA_intersect_bed = f"../../data/output/{args.file_names}/TATA/{args.promoterpref}_TATA_intersect.bed"

    # make directory for the plots to be exported to
    dirName = f"../../data/output/{args.file_names}/TATA"
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory ", dirName, " created")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

    # make directory for the plots to be exported to
    dirName = f"../../data/output/{args.file_names}/TATA/plots"
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory ", dirName, " created")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

    # make directory for the plots to be exported to
    dirName = f"../../data/output/{args.file_names}/TATA/gat_analysis"
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory ", dirName, " created")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

    # sort data
    merged = sort_data(args.promoter_bed_file, args.gene_categories)
    # create output files for gat analysis
    prepare_gat(
        merged,
        promoter_TATA_intersect_bed,
        args.TATA_box_locations,
        args.file_names,
        args.output_genecat_prefix,
        args.promoterpref,
        args.variable1_name,
        args.variable2_name,
    )


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
