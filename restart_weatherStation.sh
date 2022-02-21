#!/bin/sh

pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`

if [ "$pid" ];  then
    echo "Killing WeatherStation $pid"
    kill $pid
fi

python weatherStation_main.py &
