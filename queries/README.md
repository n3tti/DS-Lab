# Query Examples on the Dataset

This document provides examples of SQL queries applied to the dataset. 
The code for each query can be found in exemple_queries.py

## Query 1: Given a page, get same pages in different languages.

| SQL Query                   | Query Result          |
|--------------------------------------|-------------------------------|
|<pre>SELECT cousin_urls_dict <br> &emsp;FROM scraped_pages<br>&emsp; WHERE id == {id} <br>&emsp; LIMIT 1; <br></pre>| 
<pre> Cousin pages of https://www.bk.admin.ch/bk/de/home.html :<br> &emsp;de : https://www.bk.admin.ch/bk/de/home.html<br> &emsp;en : https://www.bk.admin.ch/bk/en/home.html<br> &emsp;it : https://www.bk.admin.ch/bk/it/home.html<br> &emsp;rm : https://www.bk.admin.ch/bk/rm/home.html<br> &emsp;fr : https://www.bk.admin.ch/bk/fr/home.html  </pre>|




## Get the SimHash distance between the content of two pages.

## Get pairs of pages that have a SimHash distance that is less than a certain threshold.

## Get all the pages that are referenced by a certain page.

## Get all pages that a certain page references.

## Get all referenced pdfs urls from a certain page.

## Given pdf url, get the translated pdf in all other languages available. 

## Given an image url, get the path of its stored binary file.

