# DS-Lab

To run the main crawler, in /Crawler/ run:  
scrapy crawl my2crawler -a restart=[True/False] -> restart is per default false, to set it to true run **make start RESTART=false**
If you chose restart=True, don't forget to delete the files in the JOBDIR : 
rm -r .\adminch_crawler\persistance\jobdir\* (so that the spider can restart from zero)
If restart=False, the crawler will resume the crawling process where it was left. You can cleanly stop the process (for it to be resumed later) with ONE ctrl-C.

To run the test file run the cmd "make test".