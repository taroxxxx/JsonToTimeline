# -*- coding: utf-8 -*-

"""
json から timeline html を作成

.py < .json
cd /d "/JsonToTimeline"
"/python.exe" "main.py" "/test.json"
"""

import os
import re
import sys
import glob
import time
import json
import codecs
import logging
import datetime
import traceback

from operator import itemgetter

import _lib as lib


def get_normal_timeline_row_list( timeline_item_dict_list ):

    all_timeline_row_list = []

    for timeline_item_dict in timeline_item_dict_list:

        label = timeline_item_dict[ 'row' ]
        name = timeline_item_dict[ 'bar' ]

        start_d = lib.date_str_to_datetime( timeline_item_dict[ 's' ] )
        start_d = datetime.datetime( start_d.year,start_d.month,start_d.day,0,0,0 ) # 0:00
        start_time = lib.datetime_to_time( start_d )

        end_d = lib.date_str_to_datetime( timeline_item_dict[ 'e' ] )
        end_d = datetime.datetime( end_d.year,end_d.month,end_d.day,23,59,59 ) # 終日
        end_time = lib.datetime_to_time( end_d )

        # tooltip start
        tooltip_list = [

            u'{0}{1}{0}'.format(
                r'&nbsp;',
                u'<b>{0}: {1}</b>'.format( label, name )
            ),

            u'{0}<b>date: </b>{1} - {2}{0}'.format(
                r'&nbsp;',
                lib.src_time_to_str( start_time ),
                lib.src_time_to_str( end_time )
            ), # datetime

            u'{0}<b>duration: </b>{1}{0}'.format(
                r'&nbsp;',
                lib.time_range_to_elapsed_str( start_time, end_time )
            ) # duration

        ]

        if timeline_item_dict.has_key( 'note' ):
            tooltip_list.append( timeline_item_dict[ 'note' ] )

        tooltip = '<hr>'.join( tooltip_list )

        all_timeline_row_list.append(
            lib.get_timeline_row(
                u'{0}'.format( label ),
                u'{0}'.format( name ),
                tooltip,
                start_time, end_time,
            )
        )

    return all_timeline_row_list


def get_weekday_timeline_row_list( timeline_item_dict_list ):

    """
    宅配時間用: 曜日ごとの timeline を作成

    returns:
    @all_timeline_row_list
    """

    week_day_list = [ u'月',u'火',u'水',u'木',u'金',u'土',u'日' ]

    all_timeline_row_item_list = []

    for timeline_item_dict in timeline_item_dict_list:

        start_d = lib.date_str_to_datetime( timeline_item_dict[ 's' ] )
        start_d = datetime.datetime(
            start_d.year,start_d.month,start_d.day, start_d.hour,start_d.minute,0
        )

        weekday_index = start_d.weekday()
        label = week_day_list[ weekday_index ] # 曜日ラベル
        name = timeline_item_dict[ 'row' ]

        # 曜日ラベル用に同一の日時に
        tmp_start_d = datetime.datetime(
            2000,1,1, start_d.hour,start_d.minute,0
        )

        start_time = lib.datetime_to_time( tmp_start_d )
        end_time = start_time + 60*5 # add 5min

        # tooltip start
        tooltip_list = [

            u'{0}{1}{0}'.format(
                r'&nbsp;',
                lib.src_time_to_str(
                    lib.datetime_to_time( start_d ), tmp=u'{month}/{day}({weekday_utf}) {hour}:{min}'
                )
            ), # datetime

            u'{0}{1}{0}'.format(
                r'&nbsp;',
                u'{0}'.format( timeline_item_dict[ 'bar' ] ) # 時間指定
            ),

        ]

        if timeline_item_dict.has_key( 'note' ):
            tooltip_list.append(
                u'{0}{1}{0}'.format(
                    r'&nbsp;',
                    timeline_item_dict[ 'note' ] # 品目など
                )
            )

        tooltip = '<hr>'.join( tooltip_list )

        all_timeline_row_item_list.append(
            [
                weekday_index,
                lib.get_timeline_row(
                    u'{0}'.format( label ),
                    u'{0}'.format( name ),
                    tooltip,
                    start_time, end_time,
                )
            ]
        )

    # 曜日順に並べる
    all_timeline_row_item_list = sorted( all_timeline_row_item_list, key=itemgetter( 0 ) )

    return [ item[1] for item in all_timeline_row_item_list ]


def write_html( json_file_path, mode='normal' ):

    """
    json から timeline html を作成

    args:
    s@json_file_path:

    s@mode:

    normal = s-e (yyyy-mm-dd)

    weekday = start (yyyy-mm-dd hh:mm) 曜日ごとに

    returns:
    s@html_file_path:
    """

    timeline_item_dict_list = []

    with open( json_file_path, 'r' ) as f:
        timeline_item_dict_list = json.load( f )

    all_timeline_row_list = []
    if mode == 'normal':
        all_timeline_row_list = get_normal_timeline_row_list( timeline_item_dict_list )
    elif mode == 'weekday':
        all_timeline_row_list = get_weekday_timeline_row_list( timeline_item_dict_list )

    # write html
    cur_dir_path = os.path.dirname( json_file_path )
    basename = os.path.basename( json_file_path )
    basename, ext = os.path.splitext( basename )

    html_file_path = os.path.join( cur_dir_path, r'{0}.html'.format( basename ) )

    html_fmt_dict = {
        'title' : 'timelineSlientState',
        'chart_name' : 'timelineSlientState',
        'data_line' : ',\n'.join( all_timeline_row_list ),
        'colors' : '',
        'width' : 0, # ブラウザーの幅に依存
        'height' : 900
    }

    html_line_tmp = lib.get_html_line_tmp()
    timeline_data_line_tmp = lib.get_html_timeline_data_line_tmp()
    chart_body_line_tmp = lib.get_html_chart_body_line_tmp()

    html_line = html_line_tmp.format( **{
        'title': basename.upper(),
        'timeline_line' : timeline_data_line_tmp.format( **html_fmt_dict ),
        'timeline_body_line' : chart_body_line_tmp.format( **html_fmt_dict ),
    } )

    with codecs.open( html_file_path, 'w', 'utf-8' ) as f:
        f.write( html_line )

    return html_file_path


if __name__ == '__main__':

    try:
        if 2 <= len( sys.argv ):
            if 2 <= len( sys.argv ):
                write_html( sys.argv[1], mode=sys.argv[2] )
            else:
                write_html( sys.argv[1] )
        else:
            logging.error( 'input .json file' )
            raw_input( '--- end ---' )
    except:
        logging.error( traceback.format_exc() )
        raw_input( '--- end ---' )
