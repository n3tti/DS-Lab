# Query Examples on the Dataset

This document provides examples of SQL queries applied to the dataset. 

## Given a page, get same pages in different languages.

| SQL Query (Left)                     | Query Result (Right)          |
|--------------------------------------|-------------------------------|
| ```sql                                |                               |
| SELECT DISTINCT json_each.key         | Key1                          |
| FROM your_table, json_each(cousin_urls_dict); | Key2                          |
| ```                                   | Key3                          |




## Get the SimHash distance between the content of two pages.

## Get pairs of pages that have a SimHash distance that is less than a certain threshold.

## Get all the pages that are referenced by a certain page.

## Get all pages that a certain page references.

## Get all referenced pdfs urls from a certain page.

## Given pdf url, get the translated pdf in all other languages available. 

## Given an image url, get its binary file.

