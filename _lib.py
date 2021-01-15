# -*- coding: utf-8 -*-

"""
.. note::
"""

import os
import re
import json
import time
import logging
import datetime
import subprocess


def time_to_datetime( src_time ):

    """
    time@src_time
    """
    return datetime.datetime.fromtimestamp( src_time )


def datetime_to_time( src_d ):

    """
    datetime@src_d
    """
    return time.mktime( src_d.timetuple() )


def src_time_to_str( src_time, tmp=u'{month}/{day}({weekday_utf})' ):

    """
    # 入力時間をテキストで返す

    i@src_time : time
    s@tmp : テキストテンプレート
    """

    d = datetime.datetime.fromtimestamp( src_time )

    fmt_dict = {

        'year' : d.year,
        'y' : str( d.year )[2:],
        'month' : d.month,
        'day' : d.day,
        'weekday' : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d.weekday()],
        'weekday_utf' : [u'月',u'火',u'水',u'木',u'金',u'土',u'日'][d.weekday()],
        'hour' : '{0:02d}'.format( d.hour ),
        'min' : '{0:02d}'.format( d.minute ),
        'sec' : '{0:02d}'.format( d.second ),
        'microsec' : d.microsecond,

    }

    return tmp.format( **fmt_dict ) if src_time else '-'*5


def time_range_to_elapsed_str( start_time_sec, end_time_sec=None, day_disp=1, tmp='{hour:02d}:{min:02d}' ):

    """
    # 開始>終了 までの時間をテキストで返す

    i@start_time_sec : 開始 time
    i@end_time_sec : 終了 time
    i@day_disp : 0 では 経過時間、1 では　経過日数+時間 を表示
    s@tmp : テキストテンプレート
    """

    if end_time_sec == None:
        end_time_sec = time.time()

    elapsed_sec = ( end_time_sec - start_time_sec )
    elapsed_sec = 0.0 if elapsed_sec < 0.0 else elapsed_sec

    d = datetime.timedelta( seconds=elapsed_sec )

    min = d.seconds / ( 60 )

    days_str = '{0}days&'.format( d.days ) if day_disp and elapsed_sec > 60 * 60 * 24 * 1 else '' # over 1 days

    fmt_dict = {
        'hour' :( min / 60 ) if day_disp else 24 * d.days + ( min / 60 ),
        'min' : min % ( 60 ),
        'sec' : d.seconds % ( 60 ),
    }

    return '{0}{1}'.format( days_str, tmp.format( **fmt_dict ) )


def get_html_line_tmp():

    html_line_tmp = u'''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>{title}</title>
<head>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">google.charts.load("current", {{packages:["timeline", "corechart"]}});</script>
{timeline_line}
</head>
<body>
{timeline_body_line}
</body>
</html>
'''

    return html_line_tmp


def get_html_timeline_data_line_tmp():

    timeline_data_line_tmp = u'''\
<script type="text/javascript">
google.charts.setOnLoadCallback(drawChart);
function drawChart() {{
    var dataTable = new google.visualization.DataTable();
    dataTable.addColumn({{ type: 'string', id: 'RowLabel' }});
    dataTable.addColumn({{ type: 'string', id: 'Name' }});
    dataTable.addColumn({{ type: 'string', role: 'tooltip' }});
    dataTable.addColumn({{ type: 'date', id: 'Start' }});
    dataTable.addColumn({{ type: 'date', id: 'End' }});

    dataTable.addRows([
{data_line}
    ]);
    var options = {{
        timeline: {{
            colorByRowLabel: false, showBarLabels: true, groupByRowLabel: true,
            showRowLabels: true, rowLabelStyle: {{fontSize: 11.0}},
            showBarLabels: true, barLabelStyle: {{fontSize: 11.0}},
        }},
        backgroundColor: 'lightgray',
        avoidOverlappingGridLines: false,
        tooltip: {{isHtml: true}}{colors}
    }};
    var chart = new google.visualization.Timeline(document.getElementById('{chart_name}'));
    chart.draw(dataTable, options);
    }}
</script>
'''

    return timeline_data_line_tmp


def get_html_chart_body_line_tmp():

    chart_body_line_tmp = u'''    <div id="{chart_name}" style="height: {height}px;"></div>'''

    """
    dataTable.addColumn({{ type: 'string', role: 'tooltip' }});
    """

    return chart_body_line_tmp


def date_str_to_datetime( date_str ):

    """

    """

    y = 2000
    m = 1
    d = 1

    date_str_fmt = re.compile( r'(?P<y>[\d]+)-(?P<m>[\d]+)-(?P<d>[\d]+)' )
    date_str_search = date_str_fmt.search( date_str )

    if date_str_search != None:

        y = int( date_str_search.group( 'y' ) )
        m = int( date_str_search.group( 'm' ) )
        d = int( date_str_search.group( 'd' ) )

    h = 0
    min = 0

    date_str_fmt = re.compile( r'(?P<h>[\d]+):(?P<min>[\d]+)' )
    date_str_search = date_str_fmt.search( date_str )

    if date_str_search != None:

        h = int( date_str_search.group( 'h' ) )
        min = int( date_str_search.group( 'min' ) )

    return datetime.datetime( y,m,d, h,min )


def date_str_to_time( date_str, type='ymd' ):

    start_d = lib.date_str_to_datetime( timeline_item_dict[ 's' ] )

    if start_d != None:
        start_d = datetime.datetime( start_d.year,start_d.month,start_d.day,0,0,0 ) # 0:00
    else:
        start_d = lib.date_str_to_datetime( timeline_item_dict[ 's' ], type='hm' )
        if start_d != None:
            start_d = datetime.datetime(
                start_d.year,start_d.month,start_d.day, start_d.hour,start_d.minute,0
            )
    start_time = lib.datetime_to_time( start_d )

    return None


def get_timeline_row(
    rowlabel,
    name,
    tooltip,
    time_start,
    time_end,
):

    """
    # timeline row を返します

    s@rowlabel : timeline でのラベル
    s@name : timeline でのデータ名
    i@time_start : timeline での開始日時
    i@time_end : timeline での終了日時
    """

    start_d = time_to_datetime( time_start )
    end_d = time_to_datetime( time_end )

    fmt_dict = {
        'label' : rowlabel,
        'name' : name,

        'tooltip' : tooltip,

        'sy' : start_d.year, 'smo' : start_d.month-1, 'sd' : start_d.day,
        'sh' : start_d.hour, 'sm' : start_d.minute,

        'ey' : end_d.year, 'emo' : end_d.month-1, 'ed' : end_d.day,
        'eh' : end_d.hour, 'em' : end_d.minute,
    }

    line_tmp = u"""        ['{label}','{name}','{tooltip}',new Date({sy},{smo},{sd},{sh},{sm}),"""
    line_tmp += u"""new Date({ey},{emo},{ed},{eh},{em})]"""

    return line_tmp.format( **fmt_dict )
