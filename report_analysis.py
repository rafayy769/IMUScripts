import pandas as pd
import sys
import glob
import os
import argparse
from tabulate import tabulate, tabulate_formats
import json

# Set the display format for pandas
pd.set_option('display.float_format', '{:.5f}'.format)
data_dir = "updatedData"

# Parse the command line arguments
parser = argparse.ArgumentParser(description="Analyze the accelerometer and gyroscope data.")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true", help="show verbose output")
group.add_argument("-q", "--quiet", action="store_true", help="show only the result")

# we can either specify the device name or run the analysis for all devices. add the appropriate argument.
dev_group = parser.add_mutually_exclusive_group(required=True)
dev_group.add_argument("-d", "--device", help="the name of the device to analyze")
dev_group.add_argument("-a", "--all", action="store_true", help="analyze all devices")

# how to display the data, either using the table, or simple csv style
out_group = parser.add_mutually_exclusive_group()
out_group.add_argument("-t", "--table", action="store_true", help="display the data in a table format")
out_group.add_argument("-c", "--csv", action="store_true", help="display the data in a csv format")

args = parser.parse_args()

def start(acc_file, gyro_file):
    
    print(f"{acc_file} {gyro_file}")

    try:
        acc_data = pd.read_csv(acc_file)
    except:
        print("[ERROR] An error occured while reading the accelerometer trace. Exiting.")
        return None

    try:
        gyro_data = pd.read_csv(gyro_file)
    except:
        print("[ERROR] An error occured while reading the gyroscope trace. Exiting.")
        return None

    acc_data.columns = ['sensor','date', 'sec', 'timestamp', 'x', 'y', 'z']
    gyro_data.columns = ['sensor','date', 'sec', 'timestamp', 'x', 'y', 'z']

    # add relative timestamps to data, relative to the first accelerometer sample
    acc_t0 = acc_data['timestamp'].min()

    acc_data['relative_time'] = (acc_data['timestamp'] - acc_t0)
    gyro_data['relative_time'] = (gyro_data['timestamp'] - acc_t0)

    # get to a common time
    acc_data = acc_data[acc_data['timestamp'] >= acc_t0]
    gyro_data = gyro_data[gyro_data['timestamp'] > acc_t0]
    acc_data = acc_data.reset_index(drop=True)
    gyro_data = gyro_data.reset_index(drop=True)

    # now that the accelerometer is always behind the gyroscope, we need to align the samples, i.e. the first gyroscope sample should be right between the first and second accelerometer samples. drop the first accelerometer samples until the first gyroscope sample is right between the first and second accelerometer samples
    
    gyro_start_time = gyro_data['timestamp'].iloc[0]
    while not (acc_data['timestamp'].iloc[0] <= gyro_start_time <= acc_data['timestamp'].iloc[1]):
        acc_data = acc_data.drop(index=0).reset_index(drop=True)

    # acc_sampl_delay = acc_data['relative_time'][1] - acc_data['relative_time'][0]

    # # acc1_ts is the timestamp of the first accelerometer sample and gyro1_ts is the timestamp of the first gyroscope sample
    # if (gyro_data['relative_time'].min() - acc_data['relative_time'].min()) > (acc_sampl_delay):
    #     print("samples need alignment")
    #     # Find the index of the first row in data1 that is right behind the first gyroscope sample
    #     index_to_keep = acc_data[acc_data['relative_time'] >= gyro_data['relative_time'].min() - acc_sampl_delay].index.min()

    #     # Remove rows from data1 until the index_to_keep
    #     acc_data = acc_data.loc[index_to_keep:].reset_index(drop=True)


    acc_vals = []

    acc = acc_data['timestamp']
    gyro = gyro_data['timestamp']

    t0 = acc_t0

    for i in range(1, len(acc.values)):
        if i + 1 < len(gyro.values):

            # median is the ideal alignment point
            median = (int((acc.values[i]+acc.values[i-1])/2))

            # difference betwee, two consecutive samples (ms)
            acc_diff   = (acc.values[i] - acc.values[i - 1])

            gyro_sample_diff = (gyro.values[i] - gyro.values[i - 1])

            # difference of the gyro's timestamp from the previous accelerometer sample's timestamp
            gyro_diff = (gyro.values[i - 1] - acc.values[i - 1])

            # deviance of gyro's timestamp from the ideal point. the ideal point is the median of the two consecutive accelerometer samples, we are interested in the absolute deviation of the gyro's timestamp from this ideal point
            gyro_deviance = abs(gyro.values[i - 1] - median)
            # also measure a relative deviation, with respect to the difference between the two consecutive accelerometer samples
            gyro_deviance_rel = (gyro_deviance / (acc_diff / 2)) * 100

            # append these to store (in ms)
            acc_vals.append(list(map(lambda x: x / 1e6, [acc.values[i-1] - t0, acc.values[i] - t0, gyro.values[i - 1] - t0, median - t0, acc_diff, gyro_diff, gyro_deviance, gyro_deviance_rel * 1e6, gyro_sample_diff])))

    diff = pd.DataFrame(acc_vals)
    
    diff.columns = ['acc1', 'acc2', 'gyro1', 'acc_median', 'acc_diff', 'gyro_diff', 'abs_gyro_dev', 'rel_gyro_dev', 'gyro_sample_diff']
    diff['abs_gyro_diff'] = abs(diff['gyro_diff'])

    return diff

def getDisplayData(diff_on, diff_off, device, freq, timestamp):
    gyro_diff = diff_on['gyro_diff']
    acc_diff = diff_on['acc_diff']

    gyro_diff_off = diff_off['gyro_diff']
    acc_diff_off = diff_off['acc_diff']

    abs_gyro_dev = diff_on['abs_gyro_dev']
    rel_gyro_dev = diff_on['rel_gyro_dev']

    abs_gyro_dev_off = diff_off['abs_gyro_dev']
    rel_gyro_dev_off = diff_off['rel_gyro_dev']

    # metadata is present in metadata.json
    path = os.path.join(data_dir, device, timestamp, "metadata.json")

    table_data = (f"{device}",
        # f"{freq}",
        # f"{gyro_diff.mean():.2f}",
        # f"{(1 / acc_diff.mean()) * 1e3:.2f}-{(1 / diff_on['gyro_sample_diff'].mean()) * 1e3:.2f}",
        # f"{gyro_diff_off.mean():.2f}",
        # f"{(1 / acc_diff_off.mean()) * 1e3:.4f}",
        f"{abs_gyro_dev.mean():.2f}",
        f"{abs_gyro_dev_off.mean():.2f}",
        f"{rel_gyro_dev_off.mean():.4f}",
        f"{rel_gyro_dev.mean():.4f}"
        )

    return table_data

def find_files(device_name):
    # get the list of directories for the device
    device_dir = os.path.join(data_dir, device_name)
    device_runs = os.listdir(device_dir)

    # get the list of accelerometer and gyroscope files for each run
    files_list = []
    files = {}
    for run in device_runs:
        frequencies = [200]

        for frequency in frequencies:
            acc_file_on = os.path.join(device_dir, run, f"ACC_{frequency}-On.csv")
            gyro_file_on = os.path.join(device_dir, run, f"GYRO_{frequency}-On.csv")
            acc_file_off = os.path.join(device_dir, run, f"ACC_{frequency}-Off.csv")
            gyro_file_off = os.path.join(device_dir, run, f"GYRO_{frequency}-Off.csv")

            # insert in the dictionary, add new entry if one is not already there
            files[frequency] = {"On": (acc_file_on, gyro_file_on), "Off": (acc_file_off, gyro_file_off)}

        files_list.append(files)

    return files_list

devices = []
if args.all:
    devices = os.listdir(data_dir)
elif args.device:
    # check if the device exists
    if os.path.exists(os.path.join(data_dir, args.device)):
        devices.append(args.device)
    else:
        print(f"[ERROR] Device {args.device} does not exist.")
        sys.exit(1)
else:
    print("[ERROR] Please specify a device to analyze or use the --all option to analyze all devices.")
    sys.exit(1)

table_data = [("device", "Abs. Gyro Dev\n(ms)", "Abs. Gyro Dev\n(ms) - No Mag", "Rel. Gyro Dev - no mag", "Rel. Gyro Dev - with Mag")]

for device in devices:
    files_list = find_files(device)

    for files in files_list:
        for frequency, values in files.items():
            
            (acc_file_on, gyro_file_on) = values["On"]
            (acc_file_off, gyro_file_off) = values["Off"]

            timestamp = os.path.basename(os.path.dirname(acc_file_on))

            diff_on = start(acc_file_on, gyro_file_on)
            diff_off = start(acc_file_off, gyro_file_off)

            if diff_on is not None and diff_off is not None:
                table_data.append(getDisplayData(diff_on, diff_off, device, f"{frequency}", timestamp))
    
if args.table:
    print(tabulate(table_data, headers="firstrow", tablefmt="pretty"))
elif args.csv:
    print(",".join(list(map(lambda x: x.replace("\n", " "),table_data[0]))))
    for row in table_data[1:]:
        print(",".join(row))