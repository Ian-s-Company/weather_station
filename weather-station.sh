#!/bin/sh

if [ ! -z "$API_KEY_WEATHER" ]; then
  API_KEY_WEATHER=$2
fi

if [ ! -z "$API_KEY_NEWS" ]; then
  API_KEY_NEWS=$3
fi

if [ ! -z "$APP_DIR" ]; then
  APP_DIR=$4
else
  APP_DIR="/opt/weather_station"
fi

if [ ! -z "$SCREEN_SIZE" ]; then
  if [ $SCREEN_SIZE == "2.7in" ] || [ $SCREEN_SIZE == "7x5in" ]; then
    SCREEN_SIZE=$5
  else
    echo "Screen Size is invalid, using 2.7in"
    SCREEN_SIZE="2.7in"
  fi
fi

case "$1" in
  restart)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "Restarting WeatherStation and killing PID $pid"
                kill $pid
        fi
        python $APP_DIR/weatherStation_main.py -a $APP_DIR -w $API_KEY_WEATHER -n $API_KEY_NEWS -s $SCREEN_SIZE &
  ;;
  start)
        pid=`ps -ef | grep weatherStation | grep python | grep -v grep | awk '{ print $2 }'`
        if [ "$pid" ];  then
                echo "WeatherStation is running, won't start"
        else
                echo "Starting Weather Station"
                python $APP_DIR/weatherStation_main.py -a $APP_DIR -w $API_KEY_WEATHER -n $API_KEY_NEWS -s $SCREEN_SIZE &
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
        echo "No arguments. Need (start|stop|restart) $API_KEY_WEATHER $API_KEY_NEWS $APP_DIR $SCREEN_SIZE (7.5in or 2.7in) &"
esac
