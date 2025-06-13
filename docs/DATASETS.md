# Disaster Dataset Sources and Manual Update Instructions

This project includes a collection of global disaster-related datasets stored in
Azure Blob Storage under the `disaster-impact/raw/` container. These datasets
were **manually extracted** due to the lack of stable APIs or consistent
machine-readable download endpoints.

## Manual Update Process

Most sources do not provide stable APIs or bulk data endpoints. Therefore, to
update any of the datasets:

1. Visit the source link listed in the table below.
2. Locate and download any new records since the last extraction.
3. Either:
   - Append new entries to the existing CSVs stored in the Azure blob or local, or
   - Replace the file entirely with a newly exported version.
4. Upload updated files to the correct path inside the
   `disaster-impact/data/` container.

**Important**: Always preserve the folder structure to avoid breaking downstream
processes.

## API-Based Dataset: GDACS

The GDACS dataset is unique in that it provides an official API, made available directly by the GDACS team.

To update this dataset:

1. Modify the date range in the `src/gdacs/data_acquisition_api.py` script and the `main` method.
2. Run the following command:

    ```sh
    make run_gdacs_download
    ```

This process will automatically download and save the updated records to the appropriate location.

## Web-Scraped Legacy Datasets (Now Blocked or Fragile)

Some datasets were initially extracted using automated **web scraping scripts**.
These techniques are no longer reliable or allowed due to changes in site
structure or access restrictions. The following datasets fall under this
category:

- CERF Activations
- Disaster Charter Activations
- GLIDE Events
- WFP ADAM

### How to Update These

To update any of the above, **please contact the relevant data owners** or
collaborators and request:

- API access (if available), **or**
- A recent **CSV export or database snapshot/screenshot**

Web scraping methods used previously are now deprecated and must not be reused
without permission.

## Dataset Summary

| Dataset Name                 | Source Link                                                                 | Status      | Historical Coverage | Blob Path                              | Notes                                                          |
|-----------------------------|------------------------------------------------------------------------------|-------------|----------------------|-----------------------------------------|----------------------------------------------------------------|
| Disaster Charter Activation | [https://disasterscharter.org/en/web/guest/charter-activations](https://disasterscharter.org/en/web/guest/charter-activations) | Done        | Since 2000           | `disaster-impact/raw/disaster-charter/` | Originally scraped; manual update required                     |
| CERF Activations            | [https://cerf.un.org/fundingByEmergency/all](https://cerf.un.org/fundingByEmergency/all) | Done        | Since 2006           | `disaster-impact/raw/cerf/`             | Scraping deprecated; request manual export                     |
| GLIDE Events                | [https://glidenumber.net/glide/public/search/search.jsp](https://glidenumber.net/glide/public/search/search.jsp) | Done        | Since 1930           | `disaster-impact/raw/glide/glide_events.csv` | Manual web form scrape; unstable for automation                |
| GDACS Events                | [https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH](https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH) | Done        | Since 2000           | `disaster-impact/raw/gdacs/`            | API limited                                                    |
| ADAM (WFP)                  | [https://gis.wfp.org/adamlive/](https://gis.wfp.org/adamlive/)              | Blocked     | Since 2024           | `disaster-impact/raw/wfp_adam/`         | Scraping blocked; ask WFP for data access                      |
| CEMS Copernicus             | [https://emergency.copernicus.eu/mapping/list-of-activations-rapid](https://emergency.copernicus.eu/mapping/list-of-activations-rapid) | In Progress | Since 2012           | *(pending)*                             | Has API; integration underway                                  |
| IBTrACS                     | [https://www.ncei.noaa.gov/products/international-best-track-archive](https://www.ncei.noaa.gov/products/international-best-track-archive) | Done        | Since 1842           | `disaster-impact/raw/ibtracs/IBTrACS.ALL.v04r00.nc` | Stable NetCDF source                                           |
| PDC                         | *(no public link)*                                                           | Blocked     | *(unknown)*          | *(pending)*                             | Requires account setup                                         |
| IFRC DREF                   | [https://go.ifrc.org/emergencies/all](https://go.ifrc.org/emergencies/all) | Done        | Since 2018           | `disaster-impact/raw/ifrc_dref/`        | Public CSV download                                            |
| IDMC IDUs                   | [https://helix-tools-api.idmcdb.org/external-api/idus/all/?client_id=UNOCHA01AUG22](https://helix-tools-api.idmcdb.org/external-api/idus/all/?client_id=UNOCHA01AUG22) | Done        | Since 2016           | `disaster-impact/raw/idmc_idu/`         | Stable tokenized API                                           |
| EM-DAT                      | [https://public.emdat.be/data](https://public.emdat.be/data)                | Done        | Since 2000           | `disaster-impact/raw/emdat/`            | Download from public access site                               |

## Future Datasets (Planned or Deferred)

These datasets are under consideration for future inclusion. No data has been
extracted yet.

- Dartmouth Flood Observatory
- DesInventar
- Earthquake data (GEM / USGS)
- Google FloodHub
- GloFAS
- IATI (Aid Transparency)
- FTS (Financial Tracking Service)
- EW4A (Evaluation of Early Warning)

---

Please follow the established folder structure and naming convention when
contributing additional datasets to maintain consistency across the project.
