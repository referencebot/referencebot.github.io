#!/bin/bash

git clone --recursive --branch ${VERSION} https://github.com/IATI/IATI-Standard-SSOT.git
git clone https://github.com/IATI/IATI-Developer-Documentation.git
git clone https://github.com/IATI/IATI-Guidance.git
cd IATI-Standard-SSOT
pip install -r requirements.txt
git clone https://github.com/IATI/IATI-Websites.git
rm -rf ${REPO_NAME}
git clone --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
cd IATI-Extra-Documentation/en
ln -s ../../IATI-Websites/iatistandard/_templates/ ./
ln -s ../../IATI-Websites/iatistandard/_static/ ./
cd ../..
mkdir docs
cd docs
git init
