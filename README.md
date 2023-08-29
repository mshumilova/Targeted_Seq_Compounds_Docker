#### Targeted_Seq_Compounds_Docker

###### When running the container, provide the path to the 'config.py'
docker run -v /path/to/customer/config.py:/config/config.py your-image-name


docker run -v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/script/config.py:/config compounds


docker run -v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/project_compound:/parent_dir /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/data:/input_dir compounds

docker run --privileged -it --rm \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/project_compound:/parent_dir \
-v /Users/mariashumilova/Documents/bioinf/my_projects/fin_pd/data:/input_dir \
-e PARENT_DIR=/parent_dir -e INPUT_DIR=/input_dir \
compounds


