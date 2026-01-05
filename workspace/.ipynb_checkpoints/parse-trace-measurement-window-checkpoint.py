import glob
import json
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()

measurement_window = 5000

data = []
for f in glob.glob(f"{args.path}/*.json"):
    with open (f, "r") as fh:
        data.extend(json.load(fh))

min_ts = data[0]['timestamps'][0]['ns']/1e6
max_ts = data[-1]['timestamps'][0]['ns']/1e6

sids = np.unique([data[i]['id'] for i in range(len(data))])

samples = []
#for each sample get the event names and timestamps (ms) from the moment the first req arrives (min_ts)
#put all samples in a list - each sample has tuples (event, timestamp(ms))
for sidx in sids:
    s = [(data[i]['timestamps'][0]['name'], data[i]['timestamps'][0]['ns']/1e6 - min_ts) for i in range(len(data)) if data[i]['id']==sidx and 'timestamps' in data[i].keys()]
    samples.append(s)

event_list = []
for i in range(len(samples)):
  for event in samples[i]:
    new_dict = {'id':i, 'name':event[0], 'time_ms':event[1]}
    event_list.append(new_dict)
event_list.sort(key=lambda x: x['time_ms'])

samples_dict = []

for sidx in sids:
    sample_dict = {
        data[i]['timestamps'][0]['name']: data[i]['timestamps'][0]['ns'] / 1e6 - min_ts
        for i in range(len(data))
        if data[i]['id'] == sidx and 'timestamps' in data[i]
    }
    samples_dict.append(sample_dict)

last_ts = (max_ts - min_ts) - measurement_window
samples_sub = [s for s in samples_dict if s['REQUEST_START'] >= last_ts]

queue_times = [s['COMPUTE_START'] - s['QUEUE_START'] for s in samples_sub]

infer_times = [s['COMPUTE_END'] - s['COMPUTE_START'] for s in samples_sub]

print(args.path, np.mean(queue_times), np.mean(infer_times))