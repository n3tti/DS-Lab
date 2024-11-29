# Query Examples on the Dataset

This document provides examples of SQL queries applied to the dataset. 

## From a page, get pages of same content with different languages

| SQL Query (Left)                     | Query Result (Right)          |
|--------------------------------------|-------------------------------|
| ```sql                                |                               |
| SELECT DISTINCT json_each.key         | Key1                          |
| FROM your_table, json_each(cousin_urls_dict); | Key2                          |
| ```                                   | Key3                          |



# From a page, get pages of same content with different languages

# Get the hash distance of the content of two pages

# Get pairs of pages that have a simhash distance less than thresh

# Get all the pages that are referenced by a page

# Get all pages that reference a page

# From a page, get all referenced pdfs

# From a pdf, get the translated pdf in all other languages 
