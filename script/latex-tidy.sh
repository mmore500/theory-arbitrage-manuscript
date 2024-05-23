#!/bin/bash

set -e # exit with error if any of this fails
shopt -s globstar

script_dir="$(dirname "$(readlink -f "$0")")"

cd "${script_dir}"
cd ..

latexindent -w -s -c="/tmp/" -y="defaultIndent:' '" **/*.tex
