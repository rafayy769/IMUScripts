import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# comfig
pd.set_option('display.float_format', '{:.5f}'.format)

# if the script is invoked with arguments (or from run.sh)
if sys.argv[1:]:
    temp_file = open(".temp", "r")
    filenames = temp_file.readlines()
    username = sys.argv[1]
    version = sys.argv[2]
    acc_file = filenames[0].strip()
    gyro_file = filenames[1].strip()
    filename = acc_file.split("/")[3]
else:
    # acc_file = "data/DrHamad/Accelerometer_20231102_163227,SM-A505F.csv"
    # gyro_file = "data/DrHamad/Gyroscope_20231102_163227,SM-A505F.csv"
    acc_file = "data/newtry/acc.csv"
    gyro_file = "data/newtry/gyro.csv"
    version = "default"
    username = "ahmedog"
    filename = acc_file.split("/")[2]

data = "data"
data_dir = f"{data}/{username}"

# model = filename.split(",")[1][:-4]
model = "saamsoong"

# try:
data1 = pd.read_csv(acc_file)
# except:
#     print("[ERROR] An error occured while reading the accelerometer trace. Exiting.")
#     exit(1)

try:
    data2 = pd.read_csv(gyro_file)
except:
    print("[ERROR] An error occured while reading the gyroscope trace. Exiting.")
    exit(1)

data1.columns = ['sensor','date', 'sec', 'timestamp', 'x', 'y', 'z']
data2.columns = ['sensor','date', 'sec', 'timestamp', 'x', 'y', 'z']

# UNCOMMENT TO START FROM SOME LATER SECOND
# I am preferring to start from the very beginning of the file
# val_to_rem = data1['sec'].values[0]
# val_to_rem2 = data2['sec'].values[0]
# data1 = data1[data1['sec']!=val_to_rem]
# data2 = data2[data2['sec']!=val_to_rem2]

# val_to_rem = min(data1['sec'].unique()[1], data2['sec'].unique()[1])
# print(val_to_rem)
# data1 = data1[data1['sec']>=val_to_rem]
# data2 = data2[data2['sec']>=val_to_rem]

# add relative timestamps to data
t0 = min(data1['timestamp'].min(), data2['timestamp'].min())

data1['relative_time'] = (data1['timestamp'] - t0) / 1e6
data2['relative_time'] = (data2['timestamp'] - t0) / 1e6

data1 = data1.reset_index(drop=True)
data2 = data2.reset_index(drop=True)

acc_vals = []

acc = data1['timestamp']
gyro = data2['timestamp']

for i in range(1, len(gyro.values)):
    if i + 1 < len(gyro.values):

        # median is the ideal alignment point
        median = (int((acc.values[i]+acc.values[i-1])/2))

        # difference betwee, two consecutive samples
        acc_diff   = (acc.values[i] - acc.values[i - 1])

        # difference of the gyro's timestamp from the ideal point
        gyro_diff = (gyro.values[i - 1] - median)

        # append these to store (in ms)
        acc_vals.append(list(map(lambda x: x / 1e6, [acc.values[i-1] - t0, acc.values[i] - t0, gyro.values[i - 1] - t0, median - t0, acc_diff, gyro_diff])))


diff = pd.DataFrame(acc_vals)
diff.columns = ['acc1', 'acc2', 'gyro1', 'acc_median', 'acc_diff', 'gyro_diff']

# Some statistics regarding the distribution.
diff['abs_gyro_diff'] = abs(diff['gyro_diff'])

print("----- Debug Dump -----")
print(data1[['timestamp', 'relative_time']].head())
print(data2[['timestamp', 'relative_time']].head())
print(diff.head())
print()
print()

# Calculate statistics
gyro_diff = diff['gyro_diff']

# Print statistics
print("----- STATISTICS -----")
print(f'Mean Gyro Difference: {gyro_diff.mean():.2f} ms')
print(f'Mean Absolute Gyro Difference: {abs(gyro_diff).mean():.2f} ms')
print(f'Standard deviation in Gyro differences: {gyro_diff.std()}')
print(f'Min gyro diff: {abs(gyro_diff).min()}, Max gyro diff: {abs(gyro_diff).max()}')

if (abs(gyro_diff)).mean() < 2.5:
    print(" == ELIGIBLE DEVICE")

# Frequency distribution
gyro_diff_bins = pd.cut(gyro_diff, bins=4, include_lowest=True)
freq_table = pd.value_counts(gyro_diff_bins, sort=False)
freq_percent_table = (freq_table / len(diff)) * 100

print('\nFrequency Distribution Table:')
print(pd.concat([freq_table, freq_percent_table], axis=1, keys=['Frequency', 'Percentage']))

df = diff
# Plotting
# plt.figure(figsize=(12, 6))
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(18, 10))

# Scatter plot for gyro differences
sns.scatterplot(x=range(len(df)), y='gyro_diff', data=df, label='Gyro Difference', ax=ax1)
ax1.axhline(0, color='red', linestyle='--', label='Zero Difference')
ax1.set_title(f'Scatter plot of Gyro Difference - {model},{version}')
ax1.set_xlabel('Sample Index')
ax1.set_ylabel('Gyro Difference')
ax1.set_ylim([-2.6, 2.6])
ax1.set_yticks(np.arange(-2.75, 2.75, 0.25))
ax1.legend()

# Histogram for absolute gyro differences
sns.histplot(df['abs_gyro_diff'], bins=20, kde=True, color='green', label='Absolute Gyro Difference', ax=ax2)
ax2.set_title(f'Distribution of Absolute Gyro Differences - {model},{version}')
ax2.set_xlabel('Absolute Gyro Difference')
ax2.set_ylabel('Frequency')
ax2.set_xlim([-0.1, 2.5])
ax2.legend()

plt.subplots_adjust(wspace=0.3)
# plt.savefig(f"{data_dir}/{version}.png")
plt.show()
