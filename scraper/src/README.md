# Zion NPS Permit Scraper


## zionScraper.py

The bread and butter of this project. A Selenium based script designed to scrape the number of same day, and next day permits available from Zion National Park. Scrapes permits for [technical canyons](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=3)
, [overnight climbing](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=4), and [overnight camping](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=4) inside the park borders. This data is scraped nightly from an AWS ec2 instance is exported to an AWS S3 bucket.

This script returns a csv with 48 rows, for the 48 potential areas(as of writing this).

This csv is uploaded to an S3 bucket with a filename of `yyyy-mm-dd.csv`.

### Data Options

- **permit_date**
  - The date of the permit.
  - An awkward Month Year, Day format.
- **permit_count**
  - The reason we are here, the number of permits still available for the specified resource.
- **permit_area**
  - What camping/canyoneering/climbing is available.
- **scraped_datestamp**
  - The datetime the record was scraped.
- **area_id**
  - What area type is associate with the record
  - 1: Camping, 3: Canyoneering, 4: Climbing


### Example Data Formatting

permit_date | permit_count | permit_area | scraped_datestamp | area_id
------------|--------------|-------------|-------------------|--------|
October 2021, 21 | 38 | East Rim Camp Area (12) | 2021-10-21 17:15:36 | 1