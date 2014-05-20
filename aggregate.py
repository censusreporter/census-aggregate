#!/usr/bin/env python
import psycopg2
import pandas as pd 
import pandas.io.sql as pd_sql
import re
import numpy as np
import os, os.path
# assumes access to the Census Reporter database
# you can set the Postgres password for 'census' user as the
# PGPASSWORD environment variable, or edit this to pass it in 
# psycopg2.connect

def _db_conn():
    return psycopg2.connect(dbname='census',host='localhost',user='census')

def fetch_data(table_id,state,place):
    """
    Fetch a pandas dataframe of tract data from the given table_id for the given place. Returns only the data for the parts of tracts in the place (i.e. sumlevel '080'). The table_id should be directly compatible with Census Reporter's schema: beginning with 'b' or 'c' followed by digits and optionally racial iteration and Puerto Rico letters. It is your choice whether to request tables with margin of error or not ('b01001' or 'b01001_moe').

    The dataframe index will be a full 11-digit tract ID, which is not necessarily unique in the frame. (In some places, a tract is divided into three or more parts, one of which isn't in the place and the others of which are not contiguous.) It will also include the Census Reporter computed geoid for each tract/partial, which is unique, but which is not a standard.
    """

    if not re.match(r'^\d{2}$',state):
        raise Exception('invalid state')
    if not re.match(r'\d{5}', place):
        raise Exception('invalid place')
    if not re.match(r'^(b|c)\d{5,6}[a-i]?(pr)?(_moe)?$',table_id,re.IGNORECASE):
        raise Exception('invalid table id')

    sql = "select g.state || g.county || g.tract as full_tract, d.* from acs2012_5yr.%s d, acs2012_5yr.geoheader g where sumlevel = 80 and g.geoid = d.geoid and g.state = '%s' and g.place = '%s'" % (table_id, state, place)

    with _db_conn() as conn:
        df = pd_sql.read_frame(sql,conn,index_col='full_tract')
        return df

def aggregate(data,xref,groupby='area_id',pass_columns=None):
    """
    Given two pandas dataframes with compatible indexes, aggregate the data, returning a new dataframe. The index of the returned dataframe will be the 'groupby' column, which must exist in `xref`.

    Columns in data with names matching Census Reporter data columns (table id + column number) will be summed, unless they end in '_moe', in which case they'll be handled according to the method for aggregating error. (For each group, return the square root of the sum of the squared error values.) At this time, other columns in data will not be passed through.

    If xref has more columns than the groupby column, they will all be passed through. (A typical example would be a name column.) To prevent them all from being passed through, specify an empty list or a list of only the ones which should be passed for the value of pass_columns.
    """
    crossed = data.join(xref)
    by_ca = crossed.groupby(groupby)

    series_dict = {}

    if pass_columns is None:
        pass_columns = [x for x in xref.columns if x != groupby]
    for col in pass_columns:
        series_dict[col] = by_ca[col].all() # get a series back out of the groupby

    for col in data.columns:
        if re.match(r'^(b|c)\d+[a-i]?(pr)?\d{3}(_moe)?$', col):
            if col.endswith('_moe'):
                if -1 in crossed[column]: # MOE not applicable
                    series_dict[col] = by_ca[col].apply(lambda x: -1)
                else:
                    series_dict[col] = by_ca[col].apply(lambda x: np.sqrt(np.sum(np.power(x,2))))
            else:
                series_dict[col] = by_ca[col].sum()

    return pd.DataFrame(series_dict)

def all_acs_tables():
    """
    Create a generator over all of the complete (with error) ACS data tables in the ACS 5-year release.
    """
    sql = r"select table_name from information_schema.tables where table_schema = 'acs2012_5yr' and table_name like '%moe' and table_name not like 'seq%' order by table_name"

    with _db_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            for (table_id,) in cur:
                yield table_id

def aggregate_all(state,place,xref,output_dir,overwrite=False):
    """
    Generate aggregated ACS tables for the given place. At this time, only aggregates 
    census tracts in a census place.

    Arguments:
    state -- the two-digit state FIPS code (string) for the place.
    place -- the five-digit place FIPS code (string) for the place.
    xref -- a pandas DataFrame which has an index of full tract IDs (11 digits, 2 for state, 3 for county, 6 for tract). the DataFrame must also have a column, 'area_id' which
        has identifiers for the target aggregate geographies. It may optionally include other columns, for example, names matching those ids. All of those columns will be passed through to the output file.
    output_dir -- a string representing the directory in which aggregated files should be created.

    Keyword arguments:
    overwrite -- if True, generate aggregate files even if they already exist in `output_dir`. Default: False
    """
    try:
        os.makedirs(output_dir)
    except OSError:
        pass

    for table_id in all_acs_tables():
        output_file = os.path.join(output_dir,'%s.csv' % table_id)
        if overwrite or not os.path.exists(output_file):
            data = fetch_data(table_id, state, place)
            data = data.dropna()
            if len(data) > 0:
                agg = aggregate(data,xref)
                agg.to_csv(output_file,float_format="%.0f")

def fetch_table_metadata(table_id,conn=None):
    sql = """
select t.simple_table_title, t.universe, c.column_id, c.column_title, c.indent from acs2012_5yr.census_table_metadata t, acs2012_5yr.census_column_metadata c
where c.table_id = t.table_id and t.table_id = %s
"""
    local_conn = False
    if conn is None:
        conn = _db_conn()
        local_conn = True

    cursor = conn.cursor()
    cursor.execute(sql,(table_id.upper(),))
    for row in cursor:
        yield row

    if local_conn:
        conn.close()

def ratio_with_error(df,num_column,den_column):
    """
        Given a dataframe, return a new dataframe with two series: one the ratio and the other the computed MOE for the ratio. This assumes that num_column and den_column are strings and that their error columns are named with the suffix "_moe"
    """
    ratio = df[num_column]/df[den_column]
    num_error = df['%s_moe' % num_column]
    den_error = df['%s_moe' % den_column]
    error = np.sqrt((np.power(ratio,2) * np.power(den_error,2)) + np.power(num_error,2))/df[den_column]
    return pd.DataFrame({'ratio': ratio, 'ratio_error': error})

def write_metadata_files(output_dir,base_on_tables=False,overwrite=False):
    try:
        os.makedirs(output_dir)
    except OSError:
        pass
    all_tables = open(os.path.join(output_dir,'all_tables.txt'),'w')
    with _db_conn() as conn:
        for table_id in all_acs_tables():
            chk = os.path.join(output_dir,'%s.csv' % table_id)
            if base_on_tables and not os.path.exists(chk):
                continue
            table_id = table_id.replace('_moe','')
            output_file = os.path.join(output_dir,'%s.txt' % table_id)
            if overwrite or not os.path.exists(output_file):
                cursor = fetch_table_metadata(table_id,conn)
                of = open(output_file,'w')
                for ix,(table_title, universe, column_id, column_title, indent) in enumerate(cursor):
                    if ix == 0:
                        of.write(table_title); of.write('\n')
                        of.write('-' * len(table_title)); of.write('\n')
                        of.write("Universe: %s\n" % universe)
                        of.write('\n')
                    of.write('%s%s%s\n' % (column_id, ' ' * (indent + 1), column_title))
                of.close()
                all_tables.write('%s %s\n' % (table_id.upper().ljust(10), table_title))
        all_tables.close()

if __name__ == '__main__':
    xref = pd.read_csv('chi_comm_areas/xref.csv',index_col='tract',dtype={'tract': 'S11'})
    aggregate_all('17','14000',xref,'chi_comm_areas')
