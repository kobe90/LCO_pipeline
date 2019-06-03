# LCO_pipeline

# Before starting

In swift_BAT.py

1. Fill the the 'chat' list with the the list of Telegram chat IDs to be notified upon receiving a VOEvent;
2. Assign the token of your Telegram Bot the variable named 'token';
3. Fill the 'To' list with the list of the email addresses to be notified upon receiving a VOEvent.

In LCO.py

1. Fill the 'token' variable with the LCO token referring to your account
2. Fill the 'username' and 'password' variables with your LCO access credencials.

The pipeline requires the SFD library (https://github.com/adrn/SFD) to be properly installed and the SFD folder to be placed in the home directory of the user.

# Launch the pipeline
Launch 'swift_BAT.py' to start listening VOEvents.
