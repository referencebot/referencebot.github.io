#!/bin/bash
set -o nounset

if [ "${REPO_NAME}" == "IATI-Standard-SSOT" ]; then
    git clone --recursive --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
else
    git clone --recursive --branch $VERSION https://github.com/IATI/IATI-Standard-SSOT.git
fi

if [ "${REPO_NAME}" == "IATI-Developer-Documentation" ]; then
    git clone --single-branch --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
else
    git clone https://github.com/IATI/IATI-Developer-Documentation.git
fi

if [ "${REPO_NAME}" == "IATI-Guidance" ]; then
    git clone --single-branch --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
else
    git clone https://github.com/IATI/IATI-Guidance.git
fi

cd IATI-Standard-SSOT
pip install -r requirements.txt
git clone https://github.com/IATI/IATI-Websites.git


if [ "${REPO_NAME}" == "IATI-Rulesets" ] || [ "${REPO_NAME}" == "IATI-Extra-Documentation" ] || [ "${REPO_NAME}" == "IATI-Codelists" ] || [ "${REPO_NAME}" == "IATI-Websites" ]; then
    rm -rf ${REPO_NAME}
    git clone --single-branch --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
fi

if [ "${REPO_NAME}" == "IATI-Codelists-NonEmbedded" ]; then
    cd IATI-Codelists
    git clone --single-branch --branch ${HEAD_BRANCH} ${HEAD_REPO_URL} ${REPO_NAME}
    cd ..
fi

cd IATI-Extra-Documentation/en
ln -s ../../IATI-Websites/iatistandard/_templates/ ./
ln -s ../../IATI-Websites/iatistandard/_static/ ./
cd ../..
mkdir docs
cd docs
git init
