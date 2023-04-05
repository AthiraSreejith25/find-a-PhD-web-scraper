#!/bin/python3
#The above line is called a Shebang and it tells the shell to determine with what to run this file.


#importing required packages
from os import system as sys #to execute shell commands
import requests #to make HTTP requests
import time #to use time.sleep for delay
import random #to randomise delays
from bs4 import BeautifulSoup as bs #package for webscraping
import csv #to make csv output file
import re #to search patterns and edit strings
import mysql.connector #to make MySQL db using python


#keyword = input('Enter keyword: ') #enter keyword to search from findaphd.com
keyword = 'cyber security' #in our example, we search 'plasma physics'

sql_host, sql_user, sql_password = 'localhost', 'kalian', 'kalian' #use your own hostname, username and password; make sure the chosen user has the required privileges
mode = 1 #mode-1 for csv output, mode-2 for MySQL database and mode-3 for both


#proxy settings

http_proxy, https_proxy = None, None
#http_proxy, https_proxy = 'http://172.16.2.250:3128', 'https://172.16.2.250:3128' #set variables to the desired proxy and to None if none
proxy_dict = {'http':http_proxy, 'https':https_proxy}


sys('mkdir {}'.format(keyword.replace(' ','_'))) #creates directory 'data_science' to store files


url = 'https://www.findaphd.com/phds/?Keywords={}'.format(keyword.replace(' ','+'))
main_pg = requests.get(url, proxies=proxy_dict) #gets the required page and stores it as a requests.models.Response object
bs_page = bs(main_pg.content, 'html.parser') #parsed contents of main_pg


#finding the number of pages
num_page = int(list(bs_page.find(class_='pagingAreaOuter pager').find_all('li'))[-1].get_text())
'''
We find the class 'pagingAreaOuter pager' containing the pages numbers as a list and find the list elements,
using the find and find_all methods respectively. This gives a generator object which is converted into a list.
We extract text from the last element of the obtained list, using the get_text method to obtain the last page number.
'''


#initialising empty lists to store data
titles = []
details = []
links = []
unis = []


#mining data from the first page
'''
The find_all method was used to obtain all instances of the objects of the required classes.
This was followed by using the get_text method to extract data. For links, we obtain the href from the object.

From the source code, we identify the classes of the required data:
class : data
"descFrag" : details
"instDeptRow" : unis
"h4 text-dark mx-0 mb-3" : titles and link
'''

print('scraping page 1 of {}\n'.format(num_page))

#titles
unparsed_ttls = list(bs_page.find_all(class_='h4 text-dark mx-0 mb-3'))
titles += [i.get_text() for i in unparsed_ttls]

#details
unparsed_dtls = list(bs_page.find_all(class_='descFrag'))
details += [i.get_text().rstrip(' Read more') for i in unparsed_dtls]

#links
unparsed_lnks = list(bs_page.find_all(class_='h4 text-dark mx-0 mb-3'))
links += ['www.findaphd.com{}'.format(i['href']) for i in unparsed_lnks]

#unis
unparsed_unis = list(bs_page.find_all(class_='instDeptRow'))
unis += [re.sub('\n+',', ',i.get_text().strip('\n')) for i in unparsed_unis]



#mining data from the subsequent pages
if num_page > 1:

	for i in range(2,num_page+1):

		time.sleep(random.randrange(1,2)) #to avoid overwhelming the server with requests, we wait for a few seconds (the wait time can be adjusted).
						#it is randomised to appear more human (some websites block scrapers).

		url = 'https://www.findaphd.com/phds/?Keywords={}&PG={}'.format(keyword.replace(' ','+'),str(i))
		other_pg = requests.get(url,proxies=proxy_dict) #gets the required page and stores it as a requests.models.Response object
		bs_page = bs(other_pg.content, 'html.parser') #parsed contents of other_pg

		#similar to mining data from the first page

		print('scraping page {} of {}\n'.format(i,num_page))

		#titles
		unparsed_ttls = list(bs_page.find_all(class_='h4 text-dark mx-0 mb-3'))
		titles += [i.get_text() for i in unparsed_ttls]

		#details
		unparsed_dtls = list(bs_page.find_all(class_='descFrag'))
		details += [i.get_text().rstrip(' Read more') for i in unparsed_dtls]

		#links
		unparsed_lnks = list(bs_page.find_all(class_='h4 text-dark mx-0 mb-3'))
		links += ['www.findaphd.com{}'.format(i['href']) for i in unparsed_lnks]

		#unis
		unparsed_unis = list(bs_page.find_all(class_='instDeptRow'))
		unis += [re.sub('\n+',', ',i.get_text().strip('\n')) for i in unparsed_unis]

#writing data into csv file
if mode == 1 or mode == 3:

	with open('./{}/{}.csv'.format(keyword.replace(' ','_'),keyword.replace(' ','_')),'w') as file:

		write = csv.writer(file) #instantiates a csvwriter object

		write.writerow(['Sr.no','Title','Description','University','Link']) #writes fields row

		for i in range(len(titles)):

			write.writerow([i+1,titles[i],details[i],unis[i],links[i]]) #writes a row of data every iteration

#creating a database with the acquired data
if mode == 2 or mode == 3:

	mydb = mysql.connector.connect(host=sql_host, user=sql_user, password=sql_password)
	crs = mydb.cursor() #instantiates a mysql.connector.cursor object to interact with MySQL

	crs.execute('CREATE DATABASE {}_findaphd'.format(keyword.replace(' ','_'))) #creates db
	crs.execute('USE {}_findaphd'.format(keyword.replace(' ','_'))) #switches to the created db
	crs.execute('CREATE TABLE data(id varchar(255), Title varchar(255), Description varchar(500), University varchar(255), Link varchar(255))') #creates table with relevant fields

	for i in range(len(titles)):

		crs.execute('INSERT INTO data (id, Title, Description, University, Link) VALUES ("{}","{}","{}","{}","{}")'.format(str(i+1),titles[i],re.sub("""['"]""","''",details[i]),unis[i],links[i])) #creates a record of data every iteration

	mydb.commit() #saves changes done in the current MySQL session
	mydb.close() #terminates the MySQL session

#for any queries, support or to report bugs, contact:
'''
Athira Sreejith, ms18033@iisermohali.ac.in
Priyansha Verma, ms19094@iisermohali.ac.in
Sourav S, ms18084@iisermohali.ac.in
'''

#contributions:
'''
All three contributors contributed to the project equally.
'''
