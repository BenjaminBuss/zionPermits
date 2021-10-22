# Zion NPS Permit Scraper


## zionPermitScraper.py

The bread and butter of this project. A Selenium based script designed to scrape the number of same day, and next day permits available from Zion National Park. Scrapes permits for [technical canyons](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=3)
, [overnight climbing](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=4), and [overnight camping](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=4) inside the park borders. This data is scraped nightly from an AWS ec2 instance is exported to an AWS S3 bucket.

This script returns a csv with 96 rows, for the 48 potential areas(as of writing this). Each area has two rows of data, the permits available the current day, and the permits left unreserved for the next day.

### Data Options

- **permit_date**
  - The date of the permit.
  - An awkward Month Year, Day format.
- **permit_count**
  - The reason we are here, the number of permits still available for the specified resource.
- **permit_type**
  - Full or open, whether or not there are reservations available or last minute only.
- **permit_area**
  - What camping/canyoneering/climbing is available.
- **scraped_datestamp**
  - The datetime the record was scraped.
- **area_id**
  - What area type is associate with the record
  - 1: Camping, 3: Canyoneering, 4: Climbing


### Example Data Formatting

permit_date | permit_count | permit_type | permit_area | scraped_datestamp | area_id
------------|--------------|-------------|-------------|-------------------|--------|
October 2021, 21 | 38 | full | East Rim Camp Area (12) | 2021-10-21 17:15:36 | 1




### base_permit_scrapyer.py

A simple selenium webscraper designed to scrape the number of available permits from Zions canyoneering permit site[Link](https://zionpermits.nps.gov/wilderness.cfm?TripTypeID=3).


