FROM python:3.11.3

#Install required packages
RUN pip install pandas docker wget

#Install plink
RUN mkdir -p /app/plink
WORKDIR /app/plink
RUN wget https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20230116.zip
RUN unzip plink_linux_x86_64_20230116.zip
RUN chmod +x plink
RUN ln -s /app/plink/plink /usr/local/bin/plink

#Set the working dir for the rest of the application
WORKDIR /app

#Copy application files
COPY code.py hg37.py hg38.py main.py config.py /app/

#Define the volume
#VOLUME ["/config"]

#Run the main script
CMD ["python3", "main.py"]

