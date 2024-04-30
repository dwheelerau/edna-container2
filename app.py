#!/usr/bin/env python

import os
from pathlib import Path
import sys
import time
from flask import Flask, flash, request, redirect, url_for, render_template
import subprocess

from jinja2 import Template
import codecs

# setup the qiime folder structure and remove any old runs
def cleanup():
    snakemake_clean_cmd = 'snakemake --cores all --snakefile snakemake-qiime-edna2/Snakefile --directory ./snakemake-qiime-edna2/ clean'.split()
    subprocess.run(snakemake_clean_cmd, shell=False)

def setup():
    snakemake_setup_cmd = 'snakemake --cores all --snakefile snakemake-qiime-edna2/Snakefile --directory ./snakemake-qiime-edna2/ setup'.split()
    subprocess.run(snakemake_setup_cmd, shell=False)

def runner():
    print("running")
    time.sleep(10)
    return 1


# Setting up Flask
FASTQ_FOLDER = os.path.join(os.getcwd(), 'snakemake-qiime-edna2','fastq_data')
RUN_LOG_FILE = os.path.join(os.getcwd(), 'snakemake-qiime-edna2','logs', 'runlog.txt')
DATABASE_FOLDER = os.path.join(os.getcwd(), 'snakemake-qiime-edna2', 'database',
                               'qiime2-qza')
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')
print(FASTQ_FOLDER)

app = Flask(__name__, static_url_path=STATIC_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = "secret_key"

# home page
@app.route('/')
def index():
    # remove any old data
    cleanup()
    # setup dir structure
    setup()
    return render_template('index.html')

@app.route('/infer', methods=['POST'])
def upload_image():
    print("called POST")
    file_list = request.files.getlist('file')
    if len(file_list)>0: 
        for file in file_list:
            filename = os.path.basename(file.filename)
            dst = os.path.join(FASTQ_FOLDER, filename)
            file.save(dst)
        return redirect(url_for('edit_config'))

    else:
        flash('please select a dir')
        return redirect(request.url)

# config
@app.route('/config', methods=['GET', 'POST'])
def edit_config():
    if request.method == 'POST':
        print(request.files)
        if request.files['file']:
            file = request.files['file']
            filename=os.path.basename(file.filename)
            dst = os.path.join(DATABASE_FOLDER, filename)
            file.save(dst)
        else:
            # the default midori database
            dst = "database/qiime2-qza/MIDORI2_UNIQ_NUC_GB253_srRNA_QIIME-classifier.qza"
        data = {
                'name':request.form['name'],
                'fprimer':request.form['fprimer'],
                'rprimer':request.form['rprimer'],
                'tlf':request.form['tlf'],
                'tlr':request.form['tlr'],
                'maxef':request.form['maxef'],
                'maxer':request.form['maxer'],
                'truncq':request.form['truncq'],
                'chimera':request.form['chimera'],
                'classifier':dst,
                }

        with open('./snakemake-qiime-edna2/config-template.yaml') as rf:
            template = Template(rf.read(), trim_blocks=True)
        render_file = template.render(data)
        outfile = codecs.open('./snakemake-qiime-edna2/config.yaml', 'w', 'utf-8')
        outfile.write(render_file)
        outfile.close()
        # goto the pipeline running page
        return redirect(url_for('running'))
    print('called edit config')
    return render_template('config.html')

# done
@app.route('/done')
def done():
    f_path = Path("./snakemake-qiime-edna2/final_results/final-report.pdf")

    if f_path.is_file():
        return render_template('done.html')
    else:
        return render_template('done-fail.html')

@app.route('/running')
def running():
    return render_template('running.html')

@app.route('/pipeline')
def pipeline():
    snakemake_run_cmd = 'snakemake --cores all --snakefile snakemake-qiime-edna2/Snakefile --directory ./snakemake-qiime-edna2/ all'.split()
    subprocess.run(snakemake_run_cmd, shell=False)
    zip_cmd = 'zip -FSr static/results.zip snakemake-qiime-edna2'.split()
    subprocess.run(zip_cmd, shell=False)
    return "done running"

if __name__ == "__main__":
	app.debug = True
	port = 5000 
	app.run(host="0.0.0.0", debug=True, port=port)
