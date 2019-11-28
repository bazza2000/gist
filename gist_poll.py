#! /usr/bin/env python3
# -----------------------------------------------------------
# Script Name: gist_poll.py
#
# Usage:       gist_poll.py
#
# Parameters: None
#
# Description: 
# Script is used to monitor a users github gists and 
# notify when a new gist has been published.
#
# Author:  Barry Jarman
# Date:    26 Nov 2019
# Version: v1.0
# Email:   barry.jarman@bazza.biz
# -----------------------------------------------------------

import requests
import json
import time
import sys
import smtplib
from datetime import datetime

_version = 1.0
smtp_server = "localhost"
port = 60025  
sender_email = "sender@mailserver.com" # Sender Email Address
receiver_email = "your@email.com"      # Recipient Email Address
user="bazza2000" # GitHub User to check for GISTS

# Notification Preferences
# 0 = Disabled
# 1 = Enabled
console_pref = 1 # Send Notification to stdout/console
email_pref   = 1 # Send Notification via email

# Note: Due to github polling rate restrictions of 60 requests per hour for unauthenticated user,
#       However, during testing the practical limit appeared to be lower, hence the use of 70.
#       Therefore, this value can NOT be set lower than 70.
#       https://developer.github.com/v3/#rate-limiting
poll_delay = 70

# Explicitly request the v3 REST API version via the Accept header.
headers = {
    'Accept': "application/vnd.github.v3+json",
    }

def format_github_date (github_date):
  """Function to convert the GitHub date string to a more conventional readable output."""

  # fromisoformat doesnt fully support the ISO8601 date format so we have to replace the trailing Z
  created_at_tz_convert = github_date.replace("Z", "+00:00")

  # convert the formatted string into a datetime object for formatting.
  created_at_parsed = datetime.fromisoformat(created_at_tz_convert)

  # Return formatted datetime object for display.
  return created_at_parsed.strftime("%d/%b/%Y %H:%M:%S")

def check_github_user(username):
  """Check the user provided exists on github"""
  check_user_url = f"https://api.github.com/search/users?q={username}"
  try:
    response = requests.request("GET", check_user_url, headers=headers)
    if not response:
      print(f'Error Calling API\nHTTP Response Code {response.status_code}\nResponse Text: {response.text}')
      sys.exit(1)
  except requests.exceptions.RequestException as e:
    print("Error calling API: ", e)
    sys.exit(1)

  # if total_count is 1 then user exists and is unique.
  total_count = response.json()['total_count']
  if total_count == 1:
    return True
  else:
    return False

def send_email(message):
  """Function to send message and send via email"""
  
  email_body = f"""\
Subject: New GIST Alert 

{message}"""

  print (f"Attempting to send email to {receiver_email}")
  try:
      server = smtplib.SMTP(smtp_server,port)
      server.ehlo()
      server.sendmail(sender_email, receiver_email, email_body)
      print ("Email Sent Successfully.")
      return True
  except Exception as e:
      # Print any error messages to stdout
      print(e)
      return False
  finally:
      server.quit() 

 
def get_gists(username):
  """Get username's gists"""
  # public gists for the specified user
  # GET /users/:username/gists
  url = f"https://api.github.com/users/{username}/gists"
  
  try:
    response = requests.request("GET", url, headers=headers)
    # response equates to True if response was between 200 and 400, therefore, error if outside this range.
    if not response:
      print(f'Error Calling API\nHTTP Response Code {response.status_code}\nResponse Text: {response.text}')
      sys.exit(1)
  except requests.exceptions.RequestException as e:
    print("Error calling API: ", e)
    sys.exit(1)

  # Get the current number of entries (i.e. gists)
  return response

def get_num_gists(username):
  """Get count of usernames gists"""
  gists = get_gists(username)
  return len(gists.json())


if __name__ == "__main__":

  print ("Running", sys.argv[0], "Version:",_version)

  if check_github_user(user):
    print (f"User \"{user}\" exists..continuing")
  else:
    print (f"User \"{user}\" does not exist")
    sys.exit(1)

  initial_num_gists=get_num_gists(user)

  print (f"Initial number of GISTS:{initial_num_gists}")
  print (f"Waiting for new GIST.....")

  # Repeated Loop to check and display any new Gists
  # Loop until terminated with Ctrl-C
  while True:
    current_num_gists = get_num_gists(user)
    gists = get_gists(user)

    if initial_num_gists != current_num_gists:
        print ("New GIST alert: Sending Notifications")
        # Latest GIST is always the 1st element of the json response i.e. [0]
        latest_gist = gists.json()[0]
        # Take the created_at value and reformat to more conventional readable output
        created_at = format_github_date(gists.json()[0]['created_at'])
        # Gather description and html_url information from the json.
        description = gists.json()[0]['description']
        html_url    = gists.json()[0]['html_url']
        output = f"New GIST has been created by {user} at {created_at}, with description of \"{description}\", accessed at {html_url}"
        if console_pref == 1:
          # Display the new GIST information to the console.
          print (output)
        if email_pref == 1:
          # Send the new GIST information via email.
          send_email(output)
        # Update initial GIST count for next loop
        initial_num_gists = current_num_gists
    time.sleep(poll_delay)



