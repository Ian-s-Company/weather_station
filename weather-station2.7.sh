#!/bin/sh

if [ ! -z "$API_KEY_WEATHER" ]; then
  API_KEY_WEATHER=$1
fi

if [ ! -z "$API_KEY_NEWS" ]; then
  API_KEY_NEWS=$2
fi

if [ ! -z "$APP_DIR" ]; then
  APP_DIR=$3
else
  APP_DIR="/opt/weather_station"
fi

case "$1" in
  restart)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "Restarting WeatherStation and killing PID $pid"
                kill $pid
        fi
        python $APP_DIR/weatherStation_main.py $APP_DIR $API_KEY_WEATHER $API_KEY_NEWS &
  ;;
  start)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "WeatherStation is running, won't start"
        else
                echo "Starting Weather Station"
                python $APP_DIR/weatherStation_main.py $APP_DIR $API_KEY_WEATHER $API_KEY_NEWS &
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
        echo "No arguments. Need API_KEY_WEATHER and API_KEY_NEWS"
esac
