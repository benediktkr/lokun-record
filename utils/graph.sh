rrdtool graph usercount24h_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -86400 --end now \
--font DEFAULT:7: \
--title "usercount 24h" \
--watermark "`date`" \
--vertical-label "usercount" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid MINUTE:10:HOUR:1:MINUTE:120:0:%R \
--alt-y-grid --rigid \
DEF:usercount=monitor_db.rrd:usercount:MAX \
LINE1:usercount#0000FF:"usercount" \
GPRINT:usercount:LAST:"Cur\: %5.0lf" \
GPRINT:usercount:AVERAGE:"Avg\: %5.0lf" \
GPRINT:usercount:MAX:"Max\: %5.0lf" \
GPRINT:usercount:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph usercount3d_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -259200 --end now \
--font DEFAULT:7: \
--title "usercount 3d" \
--watermark "`date`" \
--vertical-label "usercount" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid MINUTE:60:HOUR:2:MINUTE:360:0:%R \
--alt-y-grid --rigid \
DEF:usercount=monitor_db.rrd:usercount:MAX \
LINE1:usercount#0000FF:"usercount" \
GPRINT:usercount:LAST:"Cur\: %5.0lf" \
GPRINT:usercount:AVERAGE:"Avg\: %5.0lf" \
GPRINT:usercount:MAX:"Max\: %5.0lf" \
GPRINT:usercount:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph usercount30d_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -2592000 --end now \
--font DEFAULT:7: \
--title "usercount 30d" \
--watermark "`date`" \
--vertical-label "usercount" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid HOUR:6:DAY:1:DAY:3:86400:%d/%m/%y \
--alt-y-grid --rigid \
DEF:usercount=monitor_db.rrd:usercount:MAX \
LINE1:usercount#0000FF:"usercount" \
GPRINT:usercount:LAST:"Cur\: %5.0lf" \
GPRINT:usercount:AVERAGE:"Avg\: %5.0lf" \
GPRINT:usercount:MAX:"Max\: %5.0lf" \
GPRINT:usercount:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph usercount1y_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -365d --end now \
--font DEFAULT:7: \
--title "usercount 1y" \
--watermark "`date`" \
--vertical-label "usercount" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid DAY:1:DAY:7:DAY:30:86400:%B \
--alt-y-grid --rigid \
DEF:usercount=monitor_db.rrd:usercount:MAX \
LINE1:usercount#0000FF:"usercount" \
GPRINT:usercount:LAST:"Cur\: %5.0lf" \
GPRINT:usercount:AVERAGE:"Avg\: %5.0lf" \
GPRINT:usercount:MAX:"Max\: %5.0lf" \
GPRINT:usercount:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \


rrdtool graph bandwidth24h_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -86400 --end now \
--font DEFAULT:7: \
--title "bandwidth 24h" \
--watermark "`date`" \
--vertical-label "bandwidth (mb/s)" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid MINUTE:10:HOUR:1:MINUTE:120:0:%R \
--alt-y-grid --rigid \
DEF:bw=monitor_db.rrd:bandwidth:MAX \
LINE1:bw#0000FF:"bandwidth" \
GPRINT:bw:LAST:"Cur\: %5.2lf" \
GPRINT:bw:AVERAGE:"Avg\: %5.2lf" \
GPRINT:bw:MAX:"Max\: %5.2lf" \
GPRINT:bw:MIN:"Min\: %5.2lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph bandwidth3d_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -259200 --end now \
--font DEFAULT:7: \
--title "bandwidth 3d" \
--watermark "`date`" \
--vertical-label "bandwidth" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid MINUTE:60:HOUR:2:MINUTE:360:0:%R \
--alt-y-grid --rigid \
DEF:bandwidth=monitor_db.rrd:bandwidth:MAX \
LINE1:bandwidth#0000FF:"bandwidth" \
GPRINT:bandwidth:LAST:"Cur\: %5.2lf" \
GPRINT:bandwidth:AVERAGE:"Avg\: %5.2lf" \
GPRINT:bandwidth:MAX:"Max\: %5.2lf" \
GPRINT:bandwidth:MIN:"Min\: %5.2lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph bandwidth30d_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -2592000 --end now \
--font DEFAULT:7: \
--title "bandwidth 30d" \
--watermark "`date`" \
--vertical-label "bandwidth" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid HOUR:6:DAY:1:DAY:3:86400:%d/%m/%y \
--alt-y-grid --rigid \
DEF:bandwidth=monitor_db.rrd:bandwidth:MAX \
LINE1:bandwidth#0000FF:"bandwidth" \
GPRINT:bandwidth:LAST:"Cur\: %5.0lf" \
GPRINT:bandwidth:AVERAGE:"Avg\: %5.0lf" \
GPRINT:bandwidth:MAX:"Max\: %5.0lf" \
GPRINT:bandwidth:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \

rrdtool graph bandwidth1y_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -365d --end now \
--font DEFAULT:7: \
--title "bandwidth 1y" \
--watermark "`date`" \
--vertical-label "bandwidth" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid DAY:1:DAY:7:DAY:30:86400:%B \
--alt-y-grid --rigid \
DEF:bandwidth=monitor_db.rrd:bandwidth:MAX \
LINE1:bandwidth#0000FF:"bandwidth" \
GPRINT:bandwidth:LAST:"Cur\: %5.0lf" \
GPRINT:bandwidth:AVERAGE:"Avg\: %5.0lf" \
GPRINT:bandwidth:MAX:"Max\: %5.0lf" \
GPRINT:bandwidth:MIN:"Min\: %5.0lf\t\t\t" \
COMMENT:"comment\:" \
