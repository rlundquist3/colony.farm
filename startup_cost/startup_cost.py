#!/usr/bin/env python2
'''Serving dynamic images with Pandas and matplotlib (using flask).'''

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

data = {'rent' : 15000, 'kg_cricket_price' : 80,
        'kg_feed_price' : 2, 'feed_per_kg' : 1.7,
        'crickets_per_kg' : 10000, 'eggs_per_female' : 200,
        'hatch_rate' : 0.5, 'start_crickets' : 5000,
        'cycle_time' : 11, 'wages' : 3000,
        'employees' : 3}
crickets = []

@app.route('/startup_cost', methods=['POST', 'GET'])
def startup_cost():
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            data[key] = float(value)

    calculate()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(range(data['cycles_to_break_even']), crickets, '-b')
    ax.set_title('Cricket population over time until break even')
    ax.set_xlabel('cycles (%s weeks)' % (data['cycle_time']))
    ax.set_ylabel('total crickets (none harvested)')
    io = StringIO()
    fig.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())

    return render_template('startup_cost.html', graph = img, data = data)

def calculate():
    data['feed_cost_kg'] = data['kg_feed_price'] * data['feed_per_kg']
    data['kg_profit'] = data['kg_cricket_price'] - data['feed_cost_kg']
    data['break_even_kg'] = (data['rent'] + data['employees'] * data['wages']) / data['kg_profit']
    data['break_even_crickets']  = data['break_even_kg'] * data['crickets_per_kg']
    data['reserve_crickets'] = data['break_even_crickets'] / (data['eggs_per_female']/2 * data['hatch_rate'] - 1)
    data['cohort_size'] = data['break_even_crickets'] + data['reserve_crickets']

    del crickets[:]
    crickets.append(data['start_crickets'])
    data['cycles_to_break_even'] = time_to_break_even()
    data['months_to_break_even'] = data['cycle_time'] * data['cycles_to_break_even']/4.

    data['seed'] = data['months_to_break_even'] * (data['wages'] * data['employees'] + data['rent'] + data['start_crickets'] * 0.02)

def time_to_break_even():
    new_crickets = crickets[-1]/2 * data['eggs_per_female'] * data['hatch_rate']
    crickets.append(new_crickets)
    if new_crickets >= data['cohort_size']:
        return len(crickets)
    else:
        return time_to_break_even()

if __name__ == '__main__':
    app.run()
