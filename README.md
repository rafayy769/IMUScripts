# IMU Data Analysis Scripts

## Description:
The repository contains scripts to install and launch the IMU data collection app on an android device, fetch the generated csv files, and perform analysis on the data. A brief description of the files is as follows:

- `app-only.sh` : The shell script to install and launch the IMU data collection app on an android device, fetch the generated csv files.
- `plot.ipynb` : The jupyter notebook to create plots for analsis of the data.
- `report_analysis.py` : A python script to generate a report of the analysis of the data.

### Usage:

- Make sure you already have `adb` installed, and an `adb` running server. Make sure android studio is not running, and run the command : `sudo adb kill-server; sudo adb start-server`
- The shell script installs and launchs each of the included apks one by one on the target device, fetches the generated csv files, and performs analysis.
- Invoke `app-only.sh` by `./app-only.sh <name>` where `name` should be the name of the person whose device we are using.
- `report_analysis.py` generates a report of the analysis of the data. See `python report_analysis.py --help` for more details.