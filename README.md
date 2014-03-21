apcs
====

Data and information on article processing and other charges paid for scholarly publication services

Introduction
------------

The Wellcome Trust released a dataset via figshare in March 2014 giving information on their funding of 
Article Processing Charges in 2012/13. This was a concatenation of information from those institutions
that have Wellcome Trust funds. It includes all papers that the Trust is aware of paying money for and
gives paper titles, in some cases Pubmed IDs and Pubmed Central IDs, and the amount paid according to 
the institution.

Data Issues
-----------

The original dataset had inconsistent names for publishers and for journals. The data also contain significant 
errors in the amounts apparently charged. Several of the figures for PLOS papers are different to 
those in the PLOS internal accounting system. At the moment these have not been corrected.

Data and Code
-------------

Running 'getarticledetails.py' takes a cleaned version of the dataset in the 'input' folder and attempts to 
link articles to corresponding information in Europe PubMed Central (http://www.ebi.ac.uk/europepmc/). The output 
dataset is saved in the 'output' folder as a CSV file. The additional information includes DOIs, citation count, 
published article title, journal name, and journal ISSN.