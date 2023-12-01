### Usage:

- Make sure you already have `adb` installed, and an `adb` running server. Make sure android studio is not running, and run the command : `sudo adb kill-server; sudo adb start-server`
- The shell script installs and launchs each of the included apks one by one on the target device, fetches the generated csv files, and performs analysis.
- Invoke `run.sh` by `./run.sh <name>` where `name` should be the name of the person whose device we are using.
- You can run analysis directly as well by `python <name> <app-version>`, where the `name` field is the one that was specified earlier to get data from a device. The `app-version` can be one of `("app-acc-gyro.apk" "app-acc-mag-grav-gyro.apk" "app-acc-mag-gyro.apk")` to specify which version's trace we need to analyze.