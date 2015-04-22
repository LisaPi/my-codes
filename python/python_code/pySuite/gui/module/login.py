#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: login.py
'''

# Get url, username password
url = '10.10.51.134'
username = 'admin'
password = 'pica8'
     
# Access to example through web page
def loginGui():
    
    '''Example:
    import time
    from login import loginGui
    browser = loginGui()
    time.sleep(3)
    browser.quit()
    '''
    import os
    import time

    from selenium import webdriver
       
    chromedriver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = chromedriver

    browser = webdriver.Chrome(chromedriver)
    browser.get('http://%s' % url)
    browser.maximize_window()
    browser.find_element_by_xpath("//input[@placeholder='Username']").send_keys(username)
    browser.find_element_by_xpath("//input[@placeholder='Password']").send_keys(password)
    browser.find_element_by_tag_name("button").click()

    time.sleep(3)

    return browser
    
# Access to example
def loginCli():
    
    '''Example:
    import time
    from login import loginCli
    cli = loginCli()
    time.sleep(3)
    cli.close()
    '''
    import paramiko
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('%s' % url,22,username,password)
    #stdin, stdout, stderr = ssh.exec_command("pwd")
    #print stdout.readlines()
    return ssh 

# Access to example through web page
def loginPha():
    
    '''Example:
    import time
    from login import loginPha
    pha = loginPha()
    time.sleep(3)
    pha.quit() 
    '''
    
    from selenium import webdriver
    import time

    browser = webdriver.PhantomJS(executable_path=r'E:\Pica8\eclipse\workspace\Gui\module\phantomjs')
    browser.get('http://%s' % url)
    browser.save_screenshot(r'E:\Pica8\eclipse\workspace\Gui\dfile\screen.png')
    browser.find_element_by_xpath("//input[@placeholder='Username']").send_keys(username)
    browser.find_element_by_xpath("//input[@placeholder='Password']").send_keys(password)
    browser.find_element_by_tag_name("button").click()
    time.sleep(3)
    #content = browser.page_source
    #print content
    
    return browser
