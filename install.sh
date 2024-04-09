#!/bin/bash
echo "clone the GUI repo used by docker"
git clone https://github.com/dwheelerau/edna-container.git

echo "changing the port number to $1"
cd edna-container
sed -i "s/5000/$1/" app.py
grep "port" app.py
chmod +x app.py

echo "clone the main run scripts and env file"
# specific tag
git clone --depth=1 --branch 'v1.0' https://dpidave@bitbucket.org/dpi_data_analytics/snakemake-qiime-edna2.git

echo "install the conda env"
cd snakemake-qiime-edna2

conda env create -f env/qiime2-2023.5-snakemake-py38-linux-conda.yml
