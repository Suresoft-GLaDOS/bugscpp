#!/bin/bash
# Usage example: ./get_coverage yara 1 3

TargetDir=$(pwd)/targets
CoverageDir=$(pwd)/coverage

[ ! -d $TargetDir ] && mkdir $TargetDir
[ ! -d $CoverageDir ] && mkdir $CoverageDir

# parameters 
project=$1
start=$2
end=$3

for version in $(seq $start $end); do
    # set variables

    FTD=$TargetDir/${project}/buggy#${version}
    OD=$CoverageDir/${project}_${version}_buggy

    if [ -d $OD ]; then
        echo $OD exists
        continue
    fi

    echo $FTD
    echo "Outputs will be saved to" $OD

    # checkout
    python defects4cpp/d++.py checkout "$project" $version --buggy --target $TargetDir

    # build
    python defects4cpp/d++.py build $FTD --coverage

    mkdir $OD
    # run tests & measure coverage
    python defects4cpp/d++.py test $FTD --coverage --output-dir $OD --case 1
done
