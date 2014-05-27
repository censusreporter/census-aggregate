import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
from collections import OrderedDict
import re
# assumes access to the Census Reporter database
# you can set the Postgres password for 'census' user as the
# PGPASSWORD environment variable, or edit this to pass it in 
# psycopg2.connect

def _db_conn():
    return psycopg2.connect(dbname='census',host='localhost',user='census')

def load_table(table_id):
    'Given a table id, load the dataframe associated, with the index col set and such.'
    table_id = table_id.lower().replace('_moe','')
    if not re.match('^(b|c)\d+[a-i]?$',table_id):
        raise Exception("bad table_id")
    return pd.read_csv('chi_comm_areas/tables/%s_moe.csv' % table_id, index_col='area_id')


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

def load_and_flatten(table_id,indent=None):
    '''Given a table_id, load the aggregated form of it and 'flatten' it to the columns at the deepest level.

    WARNING: this is not appropriate for all tables. It should be not-wrong for tables like detailed occupation (not available at the city level anyway) but some tables seem to repeat the 'total' block along with the broken out kinds. Not sure how to identify those at first. B08124 is an example. In that case, there's an indent level skipped.
    '''
    df = pd.read_csv('chi_comm_areas/tables/%s_moe.csv' % table_id.lower(),index_col='area_id')
    return flatten(df,table_id,indent)

def flatten(df, table_id,indent=None):
    md = list(fetch_table_metadata(table_id))
    if indent is None:
        indent = max(x[-1] for x in md)
    od_cols = OrderedDict()
    try:
        od_cols['area_name'] = df['area_name']
    except: pass
    for row in md:
        if row[-1] == indent:
            try:
                od_cols[row[-2]] += df[row[-3].lower()]
            except KeyError:
                od_cols[row[-2]] = df[row[-3].lower()]

    return pd.DataFrame(od_cols,index=df.index)


def scatterplot(df, x_col, y_col,fig=None):
    """Encapsulate plot with fit line

        Some maybe helpful pages.
        http://stackoverflow.com/questions/8409095/matplotlib-set-markers-for-individual-points-on-a-line
        http://stackoverflow.com/questions/15943945/annotate-scatterplot-from-a-pandas-dataframe
    """
    x = df[x_col]
    y = df[y_col]

    fit = np.polyfit(x, y, 1)
    fit_fn = np.poly1d(fit) # y = mx+b
    if fig is None:
        fig = plt.figure()
    plt.scatter(x,y)
    plt.plot(x,fit_fn(x),'--k')
    # this is a handy one liner for a scatter plot, but not sure
    # how to add the fit line to it 
    # labeling it described at http://stackoverflow.com/questions/15910019/annotate-data-points-while-plotting-from-pandas-dataframe/15911372#15911372
    # ax = df.set_index(x_col)[y_col].plot(style='o')

def find_interesting_maxes(df,tolerance=0.1):
    """Given a dataframe, loop through columns to find cases where the row with the max value doesn't have a dubious MOE. Return a dataframe with an index of tracts, with columns for estimate, error, and column."""
    stash = []
    for column in df.columns:
        if not column.startswith('area') and not column.endswith('moe'):
            nonmarginal = df[(df[column] > 0) & ((df[column + '_moe'] / df[column]) < tolerance)]
            nonmarginal = nonmarginal[['area_name', column, column + '_moe']]
            if not nonmarginal.empty:
                max_val = nonmarginal[column].max()
                margin = nonmarginal[nonmarginal[column] == max_val][column + '_moe']
                lb = max_val - margin.max() # max seems as good a way as any to get a single value when we know there's just one in there
                ub = max_val + margin.max()
                nonmarginal = nonmarginal[(nonmarginal[column] > lb) & (nonmarginal[column] < ub)]
                for ix, (name, estimate, error) in nonmarginal.iterrows():
                    stash.append([ix, name, estimate, error, column])
    return pd.DataFrame(stash,columns=['area_number', 'name', 'estimate', 'error', 'column'])

def colmap(table_id): # expects output of aggregate.fetch_table_metadata
    return dict((col.lower(),name) for (tn, uni, col,name,indent) in list(aggregate.fetch_table_metadata(table_id)))        



# per capita, etc
# http://stackoverflow.com/questions/15916612/how-to-divide-the-value-of-pandas-columns-by-the-other-column
# df.div(df.denominator_column, axis='index')