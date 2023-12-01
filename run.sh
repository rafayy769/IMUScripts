#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <user_name>"
  exit 1
fi

user_name=$1
# app_names=("app-acc-gyro.apk" "app-acc-mag-grav-gyro.apk" "app-acc-mag-gyro.apk")
app_names=("handler-uncalibrated.apk")

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

  # # Launch the app
  adb shell am start -n com.example.datalog/.MainActivity || exit 1

  sleep 1

  # Wait for the app to close
  while is_app_running; do
   sleep 1
  done
  sleep 15

  # Create a folder for each app and user
  folder_name=data/"$user_name"/"$app_name"
  mkdir -p "$folder_name"
  
  # Pull CSV files from the Downloads folder to the current directory
  echo "-- Pulling CSV files to $folder_name/"
  adb shell ls /sdcard/SensorData/*.csv | tr -d '\r' | while read -r file; do
  	adb pull "$file" "$folder_name/"
  done 

  # # Delete CSV files from the Downloads folder on the device
  echo "-- Deleted CSV files from the device"
  adb shell rm /sdcard/SensorData/*.csv || exit 1

  # Find Accelerometer and Gyroscope CSV files
  find_csv_files "$folder_name"

  # setup and call analysis.
  echo "-- Running analysis.py for $app_name"
  python3 ./analysis.py "$user_name" "$app_name"
done

echo "------"