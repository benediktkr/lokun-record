# RRD things

## Create database

1. Set system clock before `1404249680` (`2014-07-02T21:21` in ISO format).
2. Create database with
   
```
$ rrdtool create monitor_db.rrd --step 900 DS:bandwidth:GAUGE:3600:0:1000 DS:usercount:GAUGE:4000:0:1000 RRA:MAX:0.5:1:140160
$
```

3. Set system clock back to normal

## Popualte database

Initially I'm importing data from `monitor.log`. 

```
$ python monitorparser.py 
preprocessing
rrdtool...
$
```

## Create graphs

See `graph.sh`. 