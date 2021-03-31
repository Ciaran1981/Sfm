#!/bin/bash

cd $1;

find . -name '*.las' -exec cloudcompare.CloudCompare -SILENT -O {} -C_EXPORT_FMT PLY -SAVE_CLOUDS  \;
