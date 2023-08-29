import os
import wget
import shutil
import re
import pandas as pd


parent_dir = os.environ.get('PARENT_DIR')
input_directory = os.environ.get('INPUT_DIR')
selected_files = os.environ.get('SELECTED_FILES')
assembly = os.environ.get("ASSEMBLY")

if parent_dir is None or input_directory is None:
    raise ValueError("PARENT_DIR and INPUT_DIR environment variable must be set")

vep = 'vep'
plugins = 'Plugins'
cadd = 'cadd'
gnomad = 'gnomAD'
clinvar = 'clinvar'
homo_sapiens = 'homo_sapiens'

data = 'data'
inp = 'inp_vcf'
annotated_vcf = 'annotated_vcf'
out = 'out_csv'
compound = 'compound'

ref = 'ref'

vep_dir = os.path.join(parent_dir, vep)
plugins_dir = os.path.join(vep_dir, plugins)
homo_sapiens_dir = os.path.join(vep_dir, homo_sapiens)
cadd_dir = os.path.join(plugins_dir, cadd)
gnomad_dir = os.path.join(plugins_dir, gnomad)
clinvar_dir = os.path.join(plugins_dir, clinvar)

data_dir = os.path.join(parent_dir, data)
inp_dir = os.path.join(data_dir, inp)
annotated_vcf_dir = os.path.join(data_dir, annotated_vcf)
out_dir = os.path.join(data_dir, out)
out_compound_path = os.path.join(data_dir, compound)

ref_dir = os.path.join(parent_dir, ref)

if assembly == 37:
    from hg37 import hg
if assembly == 38:
    from hg38 import hg
url_ref = hg['ref_genome_url']
ref_name_gz = hg['ref_name_gz']
url_gnomad_exomes_gz = hg['url_gnomad_exomes_gz']
url_gnomad_exomes_tbi = hg['url_gnomad_exomes_tbi']
url_gnomad_genomes_gz = hg['url_gnomad_genomes_gz']
url_gnomad_genomes_tbi = hg['url_gnomad_genomes_tbi']
url_cadd_whole_genome_gz = hg['url_cadd_whole_genome_gz']
url_cadd_whole_genome_tbi = hg['url_cadd_whole_genome_tbi']
url_clinvar_gz = hg['url_clinvar_gz']
url_clinvar_tbi = hg['url_clinvar_tbi']
url_homo_sapiens_gz = hg['url_homo_sapiens_gz']

delimiter = '\t'

# 0 Docker Run Images

def docker_pull():
    cmd1 = 'docker pull dukegcb/bwa-samtools:latest'
    cmd2 = 'docker pull broadinstitute/gatk'
    cmd3 = 'docker pull ensemblorg/ensembl-vep'
    print(cmd1)
    os.system(cmd1)
    print(cmd2)
    os.system(cmd2)
    print(cmd3)
    os.system(cmd3)

# 1. Folders creating
def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
        print(f'Created directory: {directory_path}')
    else:
        print(f'Directory already exists: {directory_path}')
def folders_creating():
    print('________________STEP directory creating______________________')
    create_directory_if_not_exists(vep_dir)
    create_directory_if_not_exists(homo_sapiens_dir)
    create_directory_if_not_exists(plugins_dir)
    create_directory_if_not_exists(cadd_dir)
    create_directory_if_not_exists(gnomad_dir)
    create_directory_if_not_exists(clinvar_dir)
    create_directory_if_not_exists(data_dir)
    create_directory_if_not_exists(inp_dir)
    create_directory_if_not_exists(annotated_vcf_dir)
    create_directory_if_not_exists(out_dir)
    create_directory_if_not_exists(out_compound_path)
    create_directory_if_not_exists(ref_dir)

# 2. Reference Genome Downloading
# Reference Genome hg38
def reference_genome_downloading():
    print('________________STEP reference genome downloading______________________')
    output = os.path.join(ref_dir, ref_name_gz)

    if len([entry for entry in os.scandir(ref_dir) if not entry.name.startswith('.')]) == 0:
        wget.download(url_ref, output)
        print(f'Reference genome downloaded: {output}')
        # gunzip fna.gz for the next steps:
        cmd_gunzip = f'gunzip {output}'
        print(cmd_gunzip)
        os.system(cmd_gunzip)
        print(f'Reference genome unzipped: {ref_dir}')

        ref_name_fna = ref_name_gz.replace('.fna.gz', '.fna')
        ref_name_fasta = ref_name_fna.replace('.fna', '.fasta')
        os.replace(f'{ref_dir}/{ref_name_fna}', f'{ref_dir}/{ref_name_fasta}')

        dict_name = ref_name_fasta.replace('fasta', 'dict')
        cmd_ref_dict = f'docker run --platform=linux/amd64 -v {parent_dir}:/gatk/main_dir -it broadinstitute/gatk:4.2.6.1 \
            ./gatk CreateSequenceDictionary \
            -R /gatk/main_dir/ref/{ref_name_fasta} \
            -O /gatk/main_dir/ref/{dict_name}'
        print(f'Reference genome dictionary creating...')
        print(cmd_ref_dict)
        os.system(cmd_ref_dict)
        print(f'Reference genome dictionary creating finished')

        cmd_ref_index = f'docker run --platform=linux/amd64 -v {parent_dir}:/main_dir/ -it dukegcb/bwa-samtools:latest \
        samtools faidx /main_dir/ref/{ref_name_fasta}'
        print(f'Reference genome indexing...')
        print(cmd_ref_index)
        os.system(cmd_ref_index)
        print(f'Reference genome indexing finished')

    else:
        print(f'Reference genome probably already exists, the folder is not empty: {ref_dir}')
        cmd_ls = f'ls {ref_dir}/'
        os.system(cmd_ls)

# 3. VEP Plugins Downloading (GnomAD, CADD, ClinVar + homo_sapience)

def vep_plugins_downloading():
    print('________________STEP VEP plugins downloading______________________')

    if len([entry for entry in os.scandir(gnomad_dir) if not entry.name.startswith('.')]) == 0:
        print(f'GnomAD Exomes Plugin Downloading ...')
        wget.download(url_gnomad_exomes_gz, gnomad_dir)
        wget.download(url_gnomad_exomes_tbi, gnomad_dir)
        print(f' GnomAD Exomes Plugin Downloaded')

        print(f'GnomAD Genomes Plugin Downloading ...')
        wget.download(url_gnomad_genomes_gz, gnomad_dir)
        wget.download(url_gnomad_genomes_tbi, gnomad_dir)
        print(f' GnomAD Genomes Plugin Downloaded')
        os.system(f'ls {gnomad_dir}')
    else:
        print(f'GnomAD plugins probably already exist, the folder is not empty: {gnomad_dir}')
        cmd_gnomad_ls = f'ls {gnomad_dir}/'
        os.system(cmd_gnomad_ls)

    if len([entry for entry in os.scandir(cadd_dir) if not entry.name.startswith('.')]) == 0:
        print(f'CADD Whole Genome Plugin Downloading ...')
        wget.download(url_cadd_whole_genome_gz, cadd_dir)
        wget.download(url_cadd_whole_genome_tbi, cadd_dir)
        print(f' CADD Whole Genome Plugin Downloaded')

    else:
        print(f'CADD plugings probably already exist, the folder is not empty: {cadd_dir}')
        os.system(f'ls {cadd_dir}')

    if len([entry for entry in os.scandir(clinvar_dir) if not entry.name.startswith('.')]) == 0:
        print(f'ClinVar Plugin Downloading ...')
        wget.download(url_clinvar_gz)
        wget.download(url_clinvar_tbi, clinvar_dir)
        print(f' ClinVar Plugin Downloaded')
        os.system(f'ls {clinvar_dir}')
    else:
        print(f'ClinVar plugin probably already exists, the folder is not empty: {clinvar_dir}')
        os.system(f'ls {clinvar_dir}')

    if len([entry for entry in os.scandir(homo_sapiens_dir) if not entry.name.startswith('.')]) == 0:
        print(f'Homo_Sapiens Plugin Downloading ...')
        wget.download(url_homo_sapiens_gz, homo_sapiens_dir)
        print(f' Homo_Sapiens Plugin Downloaded')
        for gz_file in os.listdir(homo_sapiens_dir):
            if gz_file.endswith(".gz"):
                path_to_gz_file = os.path.join(homo_sapiens_dir, gz_file)
                cmd_tar_gz = f'tar xzf {path_to_gz_file}'
                os.system(cmd_tar_gz)
    else:
        print(f'Homo_Sapiens plugin probably already exists, the folder is not empty: {homo_sapiens_dir}')
        os.system(f'ls {homo_sapiens_dir}')
# 4.
def bed_to_vcf():
    print('________________ STEP .bed to .vcf converting OR copying input .vcf files to the working directory______________________')

    # Check if the customer wants to use all files or selected_files
    if selected_files is not None:
        files_to_process = selected_files
    else:
        files_to_process = os.listdir(input_directory)

    for file_name in files_to_process:
        file_path = os.path.join(input_directory, file_name)
        file_extension = os.path.splitext(file_path)[1]

        if file_extension.startswith('.vcf'): # copy .vcf file to working directory
            shutil.copy(file_path, inp_dir)

        elif file_extension.startswith('.bed'): # convert .bed to .vcf and save to working directory
            input_file = os.path.splitext(file_path)[0]
            vcf_file = os.path.join(inp_dir, os.path.basename(file_path).split('.')[0])
            cmd = f"plink \
                    --bfile {input_file} \
                    --recode vcf \
                    --out {vcf_file}"
            os.system(cmd)

# 5. VEP Annotation

def vep_annotation():
    print('________________STEP VEP annotation______________________')

    ref_file_name = []
    for ref_file in os.listdir(ref_dir):
        if ref_file.endswith(".fasta"):
            ref_file_name = ref_file

    gnomad_exomes_file_name = []
    gnomad_genomes_file_name = []
    for gnomad_file in os.listdir(gnomad_dir):
        if gnomad_file.endswith(".gz") and gnomad_file.startswith("gnomad.exomes"):
            gnomad_exomes_file_name = gnomad_file
        if gnomad_file.endswith(".gz") and gnomad_file.startswith("gnomad.genomes"):
            gnomad_genomes_file_name = gnomad_file

    clinvar_file_name = []
    for clinvar_file in os.listdir(clinvar_dir):
        if clinvar_file.endswith(".gz"):
            clinvar_file_name = clinvar_file

    cadd_whole_file_name = []
    for cadd_file in os.listdir(cadd_dir):
        if cadd_file.startswith("whole") and cadd_file.endswith(".gz"):
            cadd_whole_file_name = cadd_file

    inp_file_names_list = []
    for inp_file in os.listdir(inp_dir):
        if inp_file.endswith(".vcf"):
            inp_file_names_list.append(inp_file)
    GRCh = 'GRCh'+str(assembly)
    print("VEP annotation (gnomAD, ClinVar, CADD databases)...")
    for vcf_file_name in inp_file_names_list:
        print(vcf_file_name)
        cmd = f"docker run --platform=linux/amd64 \
        -t -i -v {parent_dir}:/opt/vep/.vep:Z ensemblorg/ensembl-vep ./vep --cache --offline --format vcf --vcf --database --force_overwrite \
        --dir_cache /opt/vep/.vep/{vep}/ \
        --dir_plugins /opt/vep/.vep/{vep}/{plugins}/ \
        --input_file /opt/vep/.vep/{data}/{inp}/{vcf_file_name} \
        --fasta /opt/vep/.vep/{ref}/{ref_file_name} \
        --output_file /opt/vep/.vep/{data}/{annotated_vcf}/{vcf_file_name} \
        --hgvs \
        --symbol \
        --polyphen b \
        --pubmed \
        --gene_phenotype \
        --pick_allele \
        --assembly {GRCh} \
        --custom /opt/vep/.vep/{vep}/{plugins}/{gnomad}/{gnomad_exomes_file_name},gnomADe,vcf,exact,0,AF_NFE \
        --custom /opt/vep/.vep/{vep}/{plugins}/{gnomad}/{gnomad_genomes_file_name},gnomADg,vcf,exact,0,AF_NFE \
        --custom /opt/vep/.vep/{vep}/{plugins}/{clinvar}/{clinvar_file_name},ClinVar,vcf,exact,0,CLNSIG,CLNREVSTAT,CLNDN,CLN,CLNACC,CLNDSDB,CLNDSDBID \
        --plugin CADD,/opt/vep/.vep/{vep}/{plugins}/{cadd}/{cadd_whole_file_name}"
        print(cmd)
        os.system(cmd)
        print("VEP annotation is finished")

# 6. .vcf to .csv
def vcf_to_csv():
    print('________________STEP .vcf to .csv converting______________________')

    vcf_files_list = []
    for vcf_file in os.listdir(annotated_vcf_dir):
        if vcf_file.endswith(".vcf"):
            vcf_files_list.append(vcf_file)

    for vcf in vcf_files_list:
        vcf_file = os.path.join(annotated_vcf_dir, vcf)
        csv_file_name = vcf.replace("vcf", "csv")
        csv_file = os.path.join(out_dir, csv_file_name)
        with open(vcf_file, "r") as vcf, open(csv_file, "w") as csv:
            print("Converting from .vcf to .csv file format...")

            dict_VEP_header = {}
            dict_VCF_header = {}

            SAMPLES_header = []

            rows = vcf.readlines()

            #1  The indexes of rows INFO, CHROM, data:

            index_VEP = 0
            index_VCF = 0
            index_DATA = 0
            counter = 0

            for el in rows:
                #VEP annotation header (index of row identification)
                if "INFO=<ID=CSQ" in el:
                    index_VEP=counter
                #vcf. file header (index of row identification)
                if "#CHROM" in el:
                    index_VCF=counter
                    index_DATA=index_VCF+1
                if index_VEP and index_VCF != 0:
                    break
                counter += 1

            #2  Tiding of the headers:

            #1) INFO_VEP:
            # making a readable format from VEP info header
            el_VEP_header = rows[index_VEP].split(":")[1].split(" ")[1].split('"')[0].split("|")

            # creating dictionary with VEP info and indexes from 0 to len VEP info
            for i in range(len(el_VEP_header)):
                dict_VEP_header.update({el_VEP_header[i]:i})

            #2) INFO_VCF:
            # creating a readable format from VCF default header (info+sample names)
            el_VCF_header = rows[index_VCF].split("#")[1].split()[:9]

            #creating dictionary with VCF default header (info+sample names) and indexes from 0 to len VCF info
            for i in range(len(el_VCF_header)):
                dict_VCF_header.update({el_VCF_header[i]:i})

            # only sample names list
            for i in range(9,len(rows[index_VCF].split("#")[1].split())):
                sample = rows[index_VCF].split("#")[1].split()[i]
                sample_changed = f"SAMPLE_{sample}" # adding a SAMPLE_ word to mark where info about samples starts
                SAMPLES_header.append(sample_changed)

            # write header into output csv file
            header_out = []
            for el in el_VCF_header[:7] + el_VEP_header + SAMPLES_header:
                header_out.append(el)

            csv.write((delimiter).join(header_out))
            csv.write("\n")

            # 4 Data manipulations:
            # 1. INFO data
            for k in range(index_DATA, len(rows)):
                data_out = []
                data = rows[k].split()
                #1) vcf data
                vcf_data_out = data[:7]
                for el_vcf in vcf_data_out:
                    data_out.append(el_vcf)
                #2) vep data
                for el in rows[k].split()[(dict_VCF_header["INFO"])].split():
                    if re.search("CSQ", el):
                        vep_data_out = el.split("=")[1].split("|")
                        for el_vep in vep_data_out:
                            data_out.append(el_vep)
                    else:
                        number_of_empty_cells = (len(dict_VEP_header) - 1)
                        vep_data_out = (number_of_empty_cells*"|").split("|")
                        for el_vep in vep_data_out:
                            data_out.append(el_vep)
                #3) sample data
                sample_data = data[9:]
                for el_sample in sample_data:
                    data_out.append(el_sample)

                csv.write((delimiter).join(data_out))
                csv.write("\n")
            print("Converting is finished")

#%%
def compound():
    print('________________STEP compound heterozygous finding______________________')
    print('Please, wait...')

    for csv_file in os.listdir(out_dir):
        path_to_csv_file = os.path.join(out_dir, csv_file)
        data_file = pd.read_csv(path_to_csv_file, sep=delimiter, low_memory=False)
        col_names = list(data_file.columns)
        samples = []
        header = []
        for el in col_names:
            if el.startswith('SAMPLE_'):
                samples.append(el)
            else:
                header.append(el)
    counter = 0
    for el in samples:
        counter += 1
        name = el.replace('SAMPLE_', '')
        header_short = header
        header_short.append(el)

        elem = data_file[((data_file[el] !="0/0") & (data_file[el] != "./."))].loc[:, header_short]
        elem = elem.rename(columns = {el:name})
        header_short.remove(el)

        compound_out = f'{out_compound_path}/{name}.csv'
        elem.to_csv(compound_out, sep=delimiter)

    print(f'Compound heterozygous analysis completed. {counter} samples have been analyzed')

