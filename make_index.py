import re
import os.path

HTML_HEAD = """
<html>
<head><title>ACS Data Aggregated by %(title)s</title></head>
<body>
<h1>ACS Data Aggregated by %(title)s</h1>
<p>Aggregated data from the 2008-2012 American Community Survey. (<a href="../index.html">huh?</a>)
</p>
"""

HTML_FOOT = """
</body>
</html>
"""

def write_index(datadir,title):
    with open(os.path.join(datadir,'all_tables.txt')) as infile:
        with open(os.path.join(datadir,'index.html'),'w') as outfile:
            outfile.write(HTML_HEAD % {'title': title})
            for line in infile:
                (table_code, title) = re.split('\s+', line, 1)
                subs = {'table_code': table_code.lower(), 'title': title}
                outfile.write("""
[<a href="%(table_code)s_moe.csv">data</a>] [<a href="%(table_code)s.txt">columns</a>] <strong>%(table_code)s</strong>: %(title)s<br>
""" % subs)


            outfile.write(HTML_FOOT)
            
if __name__ == '__main__':
    import sys
    datadir, title = sys.argv[1:3]
    if not datadir or not title:
        raise Exception("Specify a data directory and title on the commandline")
    write_index(datadir, title)

