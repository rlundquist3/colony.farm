#!/usr/bin/env python2

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas
from cStringIO import StringIO
import base64

from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

data = {'rent' : 5000, 'kg_cricket_price' : 80,
        'kg_feed_price' : 2, 'feed_per_kg' : 1.7,
        'crickets_per_kg' : 10000, 'eggs_per_female' : 200,
        'hatch_rate' : 0.5, 'start_crickets' : 5000,
        'cycle_time' : 11, 'wages' : 3000,
        'employees' : 3, 'scaling_factor' : 2,
        'months_before_rent' : 3}
crickets = []

@app.route('/startup_cost', methods=['POST', 'GET'])
def startup_cost():
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            data[key] = float(value)

    calculate()
    calculate_profit()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(range(data['cycles_to_break_even']), crickets, '-b')
    ax.set_title('Cricket population over time until break even')
    ax.set_xlabel('cycles (%s weeks)' % (data['cycle_time']))
    ax.set_ylabel('total crickets (none harvested)')

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1, 1, 1)
    ax2.plot(range(24), data['profit'], '-b')
    ax2.set_title('Profit based on scaling factor')
    ax2.set_xlabel('months')
    ax2.set_ylabel('profit ($)')

    io = StringIO()
    fig.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
    io2 = StringIO()
    fig2.savefig(io2, format='png')
    img2 = base64.encodestring(io2.getvalue())

    return render_template('costs.jade', graph = img, graph2 = img2, data = data)

def calculate():
    data['feed_cost_kg'] = data['kg_feed_price'] * data['feed_per_kg']
    data['kg_profit'] = data['kg_cricket_price'] - data['feed_cost_kg']
    data['break_even_kg'] = (data['rent'] + data['employees'] * data['wages']) / data['kg_profit']
    data['break_even_crickets']  = data['break_even_kg'] * data['crickets_per_kg']
    data['reserve_crickets'] = data['break_even_crickets'] / (data['eggs_per_female']/2 * data['hatch_rate'] - 1)
    data['minimum_cohort_size'] = data['break_even_crickets'] + data['reserve_crickets']
    # data['scaled_cohort_size'] = data['scaling_factor'] * data['minimum_cohort_size']

    del crickets[:]
    crickets.append(data['start_crickets'])
    data['cycles_to_break_even'] = time_to_break_even()
    data['months_to_break_even'] = data['cycle_time'] * data['cycles_to_break_even']/4.
    data['seed'] = (data['months_to_break_even'] - data['months_before_rent']) * (data['wages'] * data['employees'] + data['rent'])
    # cost of housing

def time_to_break_even():
    new_crickets = crickets[-1]/2 * data['eggs_per_female'] * data['hatch_rate']
    crickets.append(new_crickets)
    if new_crickets >= data['minimum_cohort_size']:
        return len(crickets)
    else:
        return time_to_break_even()

def calculate_profit():
    data['total_crickets'] = [data['minimum_cohort_size']]
    for i in range(1, 24):
        data['total_crickets'].append(data['scaling_factor'] * data['total_crickets'][-1])
    # need to Recalculate reserve each time
    data['profit_crickets'] = [x - data['minimum_cohort_size'] - data['reserve_crickets'] for x in data['total_crickets']]
    data['profit_kg'] = [x/data['crickets_per_kg'] for x in data['profit_crickets']]
    data['profit'] = [x*data['kg_profit'] for x in data['profit_kg']]

if __name__ == '__main__':
    app.run()
