#! /usr/bin/env python3
# -----------------------------------------------------------
# Script Name: test_gist_poll.py
#
# Usage:       test_gist_poll.py
#
# Parameters: None
#
# Description: 
# Script is used to test the gist_poll.py script
#
# Author:  Barry Jarman
# Date:    26 Nov 2019
# Version: v1.0
# Email:   barry.jarman@bazza.biz
# -----------------------------------------------------------

import unittest
from gist_poll import *

class TestSum(unittest.TestCase):
    from gist_poll import user
    print ("Username for valid tests taken from gist_poll.py:", user)

    def test_format_github_date(self):
        # Response should be false for invalid user
        self.assertEqual(format_github_date("2019-09-12T22:42:02Z"),"12/Sep/2019 22:42:02")
    
    def test_email(self):
        # Test emails can be sent.
        self.assertTrue(send_email("test message"),msg="Email Server may be down or blocked by firewall, routing issues.")    

    def test_get_num_gists_valid(self):   
        # Gists should be 0 or more for valid user.
        self.assertGreater(get_num_gists(user),-1,msg=f"Username provided ({user}) may not exist in github")

    def test_get_num_gists_invalid(self):
        # Response should exit with systemexit code 1 for invalid user
        with self.assertRaises(SystemExit) as cm:
            get_num_gists("randomuser27112019")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1)

    def test_get_gists_valid(self):
        # Response should be true
        self.assertTrue(get_gists(user),msg=f"Username provided ({user}) may not exist in github")

    def test_get_gists_invalid(self):
        # Response should exit with systemexit code 1 for invalid user
        with self.assertRaises(SystemExit) as cm:
            get_gists("randomuser27112019")
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1)

    def test_check_github_user_valid(self):
        # Response should be true for valid user
        self.assertTrue(check_github_user(user),msg=f"Username provided ({user}) may not exist in github")

    def test_check_github_user_invalid(self):
        # Response should be false for invalid user
        self.assertFalse(check_github_user("randomuser27112019"))

if __name__ == '__main__':
    unittest.main()