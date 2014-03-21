# Queries Europe PMC for details of articles listed in the Wellcome Trust APC spreadsheet (2012-2013)
# Tom Pollard / 19 March 2014

# Notes: 
# Should clean up types and remove nans for strings.

import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import json
import time

# Set up connection
session = requests.session()
base_url = 'http://www.ebi.ac.uk/europepmc/webservices/rest/search/query='
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100) # fixes HTTPConnectionPool error, maybe
session.mount('http://', adapter) # fixes HTTPConnectionPool error, maybe

# set directories
curdir = os.getcwd()
dir_path = { 'input': curdir + '/input/',
				 'working': curdir + '/',
				 'output': curdir + '/output/' }

# read the cleaned Wellcome spreadsheet
fname = dir_path['input']+'Wellcome_APC_Cleaned_tomp.xlsx'
apcs = pd.io.excel.read_excel(fname, 'APC')

# change datatypes
apcs = apcs.astype(object)

# add some extra columns to the dataframe 
apcs['Extracted_date'] = time.strftime('%d/%m/%Y')
apcs['PMC_Title'] = ''
apcs['PMC_DOI'] = ''
apcs['PMC_isOpenAccess'] = ''
apcs['PMC_Journal'] = ''
apcs['PMC_Pub_Year'] = ''
apcs['PMC_Pub_Type'] = ''
apcs['PMC_Citation_Count'] = ''
apcs['Notes'] = ''
apcs['howopen_licensetype'] = ''
apcs['howopen_isOA'] = ''
apcs['howopen_BY'] = ''
apcs['howopen_NC'] = ''
apcs['howopen_ND'] = ''
apcs['howopen_SA'] = ''

# get PMCID with PMID
# what i thought were PMIDs are mostly PMCIDs
def getpmcidwithpmid(pm_id):
	query_url = 'http://www.pubmedcentral.nih.gov/utils/idconv/v1.0/?ids=' + pm_id
	r = session.get(query_url)
	soup = BeautifulSoup(r.content)
	if 'invalid article' in soup.text:
		# try searching for the ID as PMCID
		query_url = 'http://www.pubmedcentral.nih.gov/utils/idconv/v1.0/?ids=' + 'PMC' + pm_id
		pm_id = np.nan # assume PMID is wrong, so clear it
		r = session.get(query_url)
		soup = BeautifulSoup(r.content)
	try:
		pmc_id = soup.record['pmcid']
	except (AttributeError,KeyError,TypeError):
		print('PMCID not found')
		pmc_id = np.nan # PCMID is unknown
	return [pm_id, pmc_id]

# get PMCID with title
def getpmcidwithtitle(base_url,art_title):
	note = 'Unable to match title to PMCID'
	art_title = art_title.replace('(','').replace(')','').replace(':','').replace('.','')
	art_title = art_title.strip()
	art_title = art_title.replace(' ','%20')
	query_url = base_url + art_title
	r = session.get(query_url)
	soup = BeautifulSoup(r.content)
	if soup.find('hitcount') and soup.hitcount.renderContents() == '1':
		try:
			pmc_id = soup.pmcid.renderContents()
			note = 'Details matched on article title'
		except (AttributeError,KeyError,TypeError):
			print('Unable to match title to PMCID')
			pmc_id = np.nan
	else:
		print('Unable to match title to PMCID')
		pmc_id = np.nan
	return [pmc_id,note]

# get details using the PMCID
def getdetailsfrompmc(base_url,apcs,row,pmc_id,pm_id):
	query_url = base_url + 'PMCID:' + pmc_id
	r = session.get(query_url)
	soup = BeautifulSoup(r.content)
	if soup.hitcount.renderContents() == '0' and type(pm_id) is str:
		# try the PMID instead
		query_url = base_url + pm_id
		r = session.get(query_url)
		soup = BeautifulSoup(r.content)
	else:
		pass	
	if soup.hitcount.renderContents() == '1':
		try:
			apcs.loc[row[0],'PMC_Title'] = soup.title.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Title'] = np.nan
		try:
			apcs.loc[row[0],'PMC_DOI'] = soup.doi.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_DOI'] = np.nan
		try:
			apcs.loc[row[0],'PMC_isOpenAccess'] = soup.isopenaccess.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_isOpenAccess'] = np.nan
		try:
			apcs.loc[row[0],'PMID'] = soup.pmid.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMID'] = np.nan
		try:
			apcs.loc[row[0],'PMC_Journal'] = soup.journaltitle.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Journal'] = np.nan
		try:
			apcs.loc[row[0],'PMC_Pub_Year'] = soup.pubyear.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Pub_Year'] = np.nan
		try:
			apcs.loc[row[0],'PMC_Pub_Type'] = soup.pubtype.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Pub_Type'] = np.nan
		try:
			apcs.loc[row[0],'PMC_Citation_Count'] = soup.citedbycount.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Citation_Count'] = np.nan
		try: 
			apcs.loc[row[0],'PMC_Journal_ISSN'] = soup.journalissn.renderContents()
		except AttributeError:
			apcs.loc[row[0],'PMC_Journal_ISSN'] = np.nan
	else:
		apcs.loc[row[0],'PMC_Title'] = np.nan
		apcs.loc[row[0],'PMC_DOI'] = np.nan
		apcs.loc[row[0],'PMC_isOpenAccess'] = np.nan
		apcs.loc[row[0],'PMID'] = np.nan
		apcs.loc[row[0],'PMC_Journal'] = np.nan
		apcs.loc[row[0],'PMC_Pub_Year'] = np.nan
		apcs.loc[row[0],'PMC_Pub_Type'] = np.nan
		apcs.loc[row[0],'PMC_Citation_Count'] = np.nan
		apcs.loc[row[0],'PMC_Journal_ISSN'] = np.nan
		apcs.loc[row[0],'Notes'] = 'PMCID not found'
	return apcs

# Get open access details from HowOpenIsIt?
def getdetailsfromhowopenisit(doi):
	response = {}
	base_url = 'http://howopenisit.org/lookup/'
	headers = {'content-type': 'application/json'}
	search_param = [{'id': doi, 'type': 'doi'}]
	r = requests.post(base_url,data=json.dumps(search_param),headers=headers)
	try: 
		results = r.json()['results'][0]
		response['type'] = results['license'][0]['type']
		response['open_access'] = results['license'][0]['open_access']
		response['BY'] = results['license'][0]['BY']
		response['NC'] = results['license'][0]['NC']
		response['ND'] = results['license'][0]['ND']
		response['SA'] = results['license'][0]['SA']
	except (AttributeError,KeyError,TypeError,IndexError):
		response['type'] = np.nan
		response['open_access'] = np.nan
		response['BY'] = np.nan
		response['NC'] = np.nan
		response['ND'] = np.nan
		response['SA'] = np.nan
	return response

# Try to get missing PMCIDs using the PMID
print('Finding PMCIDs with PMIDs...')
for row in apcs.loc[(apcs.PMCID.isnull() & apcs.PMID.notnull())].iterrows():
	pm_id = row[1]['PMID']
	pm_id = str(int(pm_id))
	print('Attempting to match PMID: ' + pm_id)
	[pm_id, pmc_id] = getpmcidwithpmid(pm_id)
	print('Matched to: ' + str(pmc_id))
	print('\n')
	apcs.loc[row[0],'PMID'] = pm_id
	apcs.loc[row[0],'PMCID'] = pmc_id

# Try to get missing PMCIDs using the title (for records missing both PMCID and PMID)
print('Finding PMCIDs with titles...')
for row in apcs.loc[(apcs.PMCID.isnull() & apcs.PMID.isnull())].iterrows():
	art_title = row[1]['Title']
	print('Attempting to match title: ' + art_title)
	[pmc_id,note] = getpmcidwithtitle(base_url,art_title)
	print('Matched to: ' + str(pmc_id))
	print('\n')
	apcs.loc[row[0],'PMCID'] = pmc_id
	apcs.loc[row[0],'Notes'] = note

# Query Europe PMC using the PMCID
print('Getting details from Europe PMC...')
for row in apcs.loc[(apcs.PMCID.notnull() | apcs.PMID.notnull())].iterrows():
	pmc_id = row[1]['PMCID']
	pm_id = row[1]['PMID']
	print('Getting details for: ' + str(pmc_id))
	# if type(pmc_id) is str and 'PMC' in pmc_id:
	# 	print pmc_id
	apcs = getdetailsfrompmc(base_url,apcs,row,pmc_id,pm_id)
	print(apcs.loc[row[0]])
	print('\n')

# How open is it?
print('Getting open access details from HowOpenIsIt?...')
apcs['PMC_DOI'] = apcs['PMC_DOI'].replace('',np.nan)
for row in apcs.loc[apcs.PMC_DOI.notnull()].iterrows():
	doi = row[1]['PMC_DOI']
	print('Getting OA details for: ' + doi)
	response = getdetailsfromhowopenisit(doi)
	apcs.loc[row[0],'howopen_licensetype'] = response['type']
	apcs.loc[row[0],'howopen_isOA'] = response['open_access']
	apcs.loc[row[0],'howopen_BY'] = response['BY']
	apcs.loc[row[0],'howopen_NC'] = response['NC']
	apcs.loc[row[0],'howopen_ND'] = response['ND']
	apcs.loc[row[0],'howopen_SA'] = response['SA']

# Export the data to CSV file
save_fname = dir_path['output'] + 'Wellcome_APCs_updated.csv'
apcs.to_csv(save_fname, sep=',', encoding='utf-8')
