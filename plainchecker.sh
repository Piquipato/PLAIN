#!/bin/bash

if [[ -z $PLAIN_ENV ]]; then
    PLAIN_ENV="/c/Users/geneticalapaz/AppData/Local/anaconda3/envs/webdriver"
fi

eval "$(conda shell.bash hook)"
conda activate "$PLAIN_ENV"

python -m plainchecker "$@"