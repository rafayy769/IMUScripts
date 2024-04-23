#!/bin/bash

# this will be used to just run the app and not the analysis
# usage will be the same

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <user_name>"
	exit 1
fi

user_name=$1
app_names=("10k.apk")

file_dump_dir="/sdcard/Download"
app_activity_name="com.example.datalog/.MainActivity"

timestamp=$(date +%s)

# Function to check if the app is running
is_app_running() {
	adb shell pidof com.example.datalog
}

# Function to find Accelerometer and Gyroscope CSV files
find_csv_files() {
	local folder="$1"
	ls "$folder"/Accelerometer*.csv 2>/dev/null > .temp
	ls "$folder"/Gyroscope*.csv 2>/dev/null >> .temp
}

# Install and launch each app
for app_name in "${app_names[@]}"; do
	echo "-- $app_name"

	# Install the app via adb
	adb install -r "$app_name" || exit 1

	# Launch the app
	adb shell am start -n $app_activity_name || exit 1
	sleep 5

	# Wait for the app to close
	while is_app_running; do
		sleep 1
	done
	sleep 1

	# try to get the device name using adb
	device_name=$(adb shell getprop ro.product.model)
	# if device name is not empty then we will use that, otherwise, we can simply use user_name as the device name
	if [ -z "$device_name" ]; then
		device_name=$user_name
	fi

	# Create a folder for each app and user, along with the timestamp
	folder_name=data/"$device_name"/"$timestamp"/"$app_name"
	mkdir -p "$folder_name"

	# Pull CSV files from the Downloads folder to the current directory
	echo "-- Pulling CSV files to $folder_name/"
	adb shell ls $file_dump_dir/*.csv | tr -d '\r' | while read -r file; do
		adb pull "$file" "$folder_name/"
	done 

	# Delete CSV files from the Downloads folder on the device
	echo "-- Deleted CSV files from the device"
	adb shell rm $file_dump_dir/*.csv || exit 1
done

echo "------"
