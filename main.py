#from code import docker_pull
from code import folders_creating
from code import reference_genome_downloading
from code import vep_plugins_downloading
from code import bed_to_vcf
from code import vep_annotation
from code import vcf_to_csv
from code import compound
from code import check_docker_availability

#docker_pull()
#_______checking if there is an empty folder or not
folders_creating()
reference_genome_downloading()
vep_plugins_downloading()
#______running without checking
bed_to_vcf()
vep_annotation()
vcf_to_csv()
compound()
check_docker_availability()