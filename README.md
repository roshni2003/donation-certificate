# 🧩 Donation Certificate Automation

This Python script automates the process of generating donor certificates by fetching data from a Google Sheet and sending it to a Google Apps Script endpoint that creates PDFs.  

It’s designed to run automatically (e.g., daily at midnight) using **cron jobs** on macOS, Linux, or Windows (via Task Scheduler).

---

## 📋 Features

✅ Fetches donor data from Google Sheets  
✅ Filters only **unprocessed donors**  
✅ Calls your **Google Apps Script API** to generate certificates  
✅ Marks donors as processed  
✅ Supports daily **automated execution via cron**  
✅ Saves logs for tracking successes and errors  

---

## ⚙️ Requirements

- Python 3.8 or higher  
- Internet access  
- A deployed **Google Apps Script Web App URL** (used as API endpoint)  

---

## 🧰 Installation Guide


### 🪟 For Ubuntu

>sudo apt update
>sudo apt install python3 python3-pip -y
>python3 --version
>pip3 --version

# Create a project folder 
>mkdir donation-certificate
>cd donation-certificate

# Create virtual environment
>python3 -m venv venv
>source venv/bin/activate  # (use venv\Scripts\activate on Windows)

# Install dependencies
pip install requests pandas openpyxl

## Set Certificate generation Automatically

# There are 3 paths involved:
1️⃣ The Python interpreter path

This is the program that runs Python scripts.
You find it with:

>which python3


✅ Example outputs:

/usr/bin/python3 → system-wide Python

/usr/local/bin/python3 → Homebrew Python

/Users/sama/venv/bin/python3 → virtual environment Python

You use exactly this path in your cron command.

2️⃣ The script file path

This is where your .py file lives.
You find it by navigating to your project folder and running:

>pwd


If your script is named certificate.py, then its full path is:

<pwd output>/certificate.py


✅ Example:
If pwd returns /home/sama/DonationAutomation,
then full script path = /home/sama/DonationAutomation/certificate.py.

3️⃣ The log file path (optional but recommended)

You decide this one — it’s just a file where output and errors are saved.

For example:

/home/sama/DonationAutomation/certificate_log.txt


This is useful to check if the job actually ran and what it printed.

⚙️ Putting it all together:

Let’s say:

Python path = /usr/bin/python3

Script path = /home/sama/DonationAutomation/certificate.py

Log file path = /home/sama/DonationAutomation/certificate_log.txt

Then your cron line will be:

>0 0 * * * /usr/bin/python3 /home/sama/DonationAutomation/certificate.py >> /home/sama/DonationAutomation/certificate_log.txt 2>&1

# Add cron job
crontab -e
# Add this line:
# Run every day at midnight
0 0 * * * /Users/sama/donation-certificate/venv/bin/python /Users/sama/donation-certificate/generate.py >> /Users/sama/donation-certificate/cron.log 2>&1
@reboot /Users/sama/donation-certificate/venv/bin/python /Users/sama/donation-certificate/generate.py >> /Users/sama/donation-certificate/cron.log 2>&1

# Save and exit (Ctrl+O + Enter, then Ctrl+X)

###### 💖 Happy Coding & Automating Certificates! 💫 ######



