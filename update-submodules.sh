#!/bin/bash 

RED_COLOR='\E[1;31m'
RES='\E[0m'

paths=()
handled=()

function findmodules() {
    result=0
    currentpath=$1
    for handle in ${handled[*]}
    do
        if [ "$handle" == "$currentpath" ]
        then
            result=1
        fi
    done
    if [ "$result" != "1" ]
    then 
        handled[${#handled[@]}]=$currentpath
        (cd $currentpath && git checkout master && git pull origin master && git submodule update --force --init --recursive)
        for path in `find $currentpath -name ".gitmodules" | awk -F '/' 'OFS="/"{$NF="";print}'`
        do
            for file in `(cd ./$path && grep -i 'path' .gitmodules | awk '{print $3}')`
            do
                echo -e "${RED_COLOR} current is into $path$file ${RES}"
                (cd $path$file && git checkout master && git pull origin master && git submodule update --force --init --recursive &&  git checkout master && git pull)
                (findmodules $path$file)
            done
        done
    fi
}

findmodules ./
