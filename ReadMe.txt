

The PyGeocode script works in the following manner:

1. Utilizes ArcGIS geocoding and creates a first run attempt of geocoded addresses. 

2. Next loops through all records with no successful match and attempts to utilize Google's geocoding web service

3. The method of geocoding is captured as either ArcGIS or Google.


Requirements Prior to Use:

1. Python 2.6-2.7 ---may work with later versions or earlier versions

2. Valid ArcGIS license for the computer which the script is run

3. Saving a copy of the script on your local computer

4. Opening the script file copy in a Text Editor and renaming the locations of:
  CHANGE LOCATIONS (as detailed in the comments of the script file)
   A. your incidents (addresses you want to geocode) file...must be csv format 
   B. address locator file 	
   C. name of desired output location...just pick a name and location on your computer
   D. change field names to those exactly occuring in your incidents file: Address and City 

Known Issues:

- Requires manual renaming of the file names.
- google allows a present maximum of 15,000 requests per 24 hours


TO DO List:

- create a database which stores and limits requests to Google in a 24 hour period
- provide a function which deidentifies the data:
	- have user identify a unique id, non-identifiable integer
	- if no unique id exists, add a new field to the table
	- create a new table for just address information
	- copy the incidents table leaving out everything but the unique id and the address information
	- geocode, then merge the results of the geocode to the identity data based on the non-identifiable unique id

- provide a user interface to Windows file locations using the Windows Browse functions, allowing users to set the Change locations in
  a familiar format

- provide a naming of address, city columns in the csv file

- accept excel files as well as csv files for the analysis
- identify junk address fields through a address analysis function.

Ideal Address analysis function would:

analyze an address string and:

	- count the number of character (checking whether it was blank or check if NULL), these would be skipped and labeled as junk
	- identify apartment data
	- identify misspellings of suffixes
	- identify junk records, i.e. a default value which has no real meaning, example: 9999 Homeless Dr


