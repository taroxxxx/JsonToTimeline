# -*- coding: utf-8 -*-

"""
.. note::
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

import _lib as lib


def write_html( json_file_path ):

    """
    json から timeline html を作成

    args:
    s@json_file_path:

    returns:
    html_file_path:
    """

    all_timeline_row_list = []

    html_line_tmp = lib.get_html_line_tmp()
    timeline_data_line_tmp = lib.get_html_timeline_data_line_tmp()
    chart_body_line_tmp = lib.get_html_chart_body_line_tmp()

    timeline_item_dict_list = []

    with open( json_file_path, 'r' ) as f:
        timeline_item_dict_list = json.load( f )

    for timeline_item_dict in timeline_item_dict_list:

        label = timeline_item_dict[ 'row' ]
        name = timeline_item_dict[ 'bar' ]

        start_d = lib.date_str_to_datetime( timeline_item_dict[ 's' ] )
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

    # write html
    cur_dir_path = os.path.abspath( r'.' )
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

    html_line = html_line_tmp.format( **{
        'title': basename.upper(),
        'timeline_line' : timeline_data_line_tmp.format( **html_fmt_dict ),
        'timeline_body_line' : chart_body_line_tmp.format( **html_fmt_dict ),
    } )

    with codecs.open( html_file_path, 'w', 'utf-8' ) as f:
        f.write( html_line )

    return html_file_path


def main():

    """
    実行
    """

    # get .csv
    cur_dir_path =  os.path.abspath( r'.' )
    json_file_path_list = glob.glob( os.path.join( cur_dir_path, r'*.json' ) )

    for json_file_path in json_file_path_list:

        write_html( json_file_path )

if __name__ == '__main__':

    try:
        main()
    except:
        logging.error( traceback.format_exc() )
        raw_input( '--- end ---' )
