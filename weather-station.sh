#!/bin/sh

CONFIG_FILE=$2

case "$1" in
  restart)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "Restarting WeatherStation and killing PID $pid"
                kill $pid
        fi
        python weatherStation_main.py -c $CONFIG_FILE &
  ;;
  start)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "WeatherStation is running, won't start"
        else
                echo "Starting Weather Station"
                python weatherStation_main.py -c $CONFIG_FILE &
        fi
  ;;
  stop)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "Killing WeatherStation, PID $pid"
                kill $pid
        else
                echo "Can't find WeatherStation PID"
        fi
  ;;
  *)
        echo "No arguments. Need (start|stop|restart) $CONFIG_FILE &"
esac
