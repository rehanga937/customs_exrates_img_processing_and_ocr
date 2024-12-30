# Intro
- This project was initiated for the data scraping process for the weekly updated exchange rates on the customs website.
- The problem was the PDFs containing the table with the exchange rates for various countries was an image. 
- While the solution deployed at Browns uses Azure Document Intelligence (excellent performance and we fit the requirements for the free tier), this is an attempt by me to use image processing to extract the cells and pass it to an offline OCR model (Tesseract).
- A while ago I tried different techniques, before ultimately settling on an inefficient system using my own algorithm to detect the table corners, k++ means clustering for row and column detection, all in combination with open-cv's contour detection. This yielded ~55% detection rate on the benchmark tool and was very slow.
- This new method uses contour detection, which I have used in a way to more reliably detext table corners, and scipy signal library find_peaks algorithm to find rows and columns. This gives ~84% detection rate.
- The most common issue remains that if the 4 corners of the table are not identifid, detection for that documents falls drastically.

# Benchmark Tool
I have made a separate benchmark tool to compare the country-exchangerate detection rate against the performance of Azure Document Intelligence (or technically anything else). Read it to see what 'detection rate' and 'detection of a country-exchangerate pair' means/

# Further improvements
- Table corner detection needs to be more reliable.
- The system for persisting images during the various processing stages to disk for debugging has been implemented in the most idiotic and annoying and bad code practice way possible, and some of them don't even work. 

# Documentation
The notebook in the testing_notebooks folder, will provide an explanation of how the thing works. I have only made few improvements over it in the main program.

# Usage
- Run main.py.
- It will scrape all links from the customs website exchange rate page. The links are listed in a dynamic table. You can set in config.py whether you want just the first page's links or all of them. You can also manipulate the links variable (a list) to just get the links you want.
