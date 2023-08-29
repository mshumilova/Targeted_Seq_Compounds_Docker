#### Targeted_Seq_Compounds_Docker

docker run --privileged -it --rm \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/project_compound:/parent_dir \
-v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/data:/input_dir \
-e PARENT_DIR=/parent_dir -e INPUT_DIR=/input_dir \
-e SELECTED_FILES=None \ 
-e ASSEMBLY=37 \
compounds


