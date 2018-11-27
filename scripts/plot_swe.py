import glob
import os
import datetime
import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import FuncTickFormatter, FixedTicker


def save_html_plot(df):

    siteId = df.columns[0]
    df = df.clip(lower=0)  # clip negative values at zero
    df = df.groupby(df.index).first()  # remove duplicates in the index
    df.index = pd.to_datetime(df.index)
    print "Generating graph for site ", siteId

    df['year'] = df.index.year
    df['doy'] = df.index.dayofyear

    df1 = df.reset_index()
    df1 = df1.pivot('doy', 'year', siteId)

    p = figure(title="Station id " + siteId, plot_width=700, plot_height=500)

    for i in range(len(df1.columns)):
        p.line(df1.index, df1.iloc[:, i], line_color='grey', line_width=1, alpha=0.25)

    this_year = datetime.datetime.now().year
    df2 = df[df['year'] == this_year]

    p.line(df2['doy'], df2[siteId], line_color='blue', line_width=2, legend='Current year')
    p.xaxis[0].ticker = FixedTicker(ticks=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366])
    p.xaxis.formatter = FuncTickFormatter(code="""
                     var labels = {'1':'Jan',32:'Feb',60:'Mar',91:'Apr',121:'May',152:'Jun',182:'Jul',213:'Aug',244:'Sep',274:'Oct',305:'Nov',335:'Dec',366:'Jan'}
                     return labels[tick];
                     """)

    p.xaxis.axis_label = 'Day of year'
    p.yaxis.axis_label = 'Snow Water Equivalent (mm)'
    p.background_fill_color = 'beige'
    p.background_fill_alpha = 0.2

    out_path = os.path.join('../graphs/swe', siteId)
    output_file(out_path + ".html")
    save(p)


def write_all_swe(swe_dat):

    dat = pd.read_csv(swe_dat, index_col='date')

    for col in dat:

        save_html_plot(dat[[col]].copy())


write_all_swe('../data/swe/snotel_swe.csv')
