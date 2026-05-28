# Irresponsible AI: big tech's influence on AI research and associated impacts

This repo contains the code for the analysis described in the paper ["Irresponsible AI: big tech's influence on AI research and associated impacts"](https://arxiv.org/abs/2512.03077) which was published as a position paper at ICML 2026. This code calculates the persentage of big tech affiliations in the papers published and NeurIPS, ICML, ICLR in 2013-2025. The scrips help to download pdf files, extract affiliations, calculate percentage of big-tech-affiliated papers and plot the final figure.

## How to use the scripts

### NeurIPS data
1. Download metadata about the papers (authors names, title, url, etc.) for each year. It creates a csv file which is used to process pdf files later. Example: `python download_neurips_metadata.py --year=2024`
2. Download pdfs of the papers for each year. Example: `python download_neurips_pdfs.py --year=2024`
3. Parse pdf files to extract affiliations, separately for each year. Example: `python parse_pdfs.py --conf=neurips --year=2024`
4. Compute statistics over all years: `python analyse_affiliations.py --conf=neurips`

### ICML data
1. Download metadata and pdfs for years 2013-2024: `python download_icml.py`
2.  Parse pdf files to extract affiliations, separately for each year. Example: `python parse_pdfs.py --conf=icml --year=2024`
3. Compute statistics over all years: `python analyse_affiliations.py --conf=icml`

### ICLR data
1. Download metadata about the papers (authors names, title, url):
    - For the years 2013-2014 and 2017-2025, directry from OpenReview: `python download_iclr_metadata.py --username=<OPENREVIEW USERNAME> --password=<OPENREVIEW PASSWORD>`
    - For the year 2015, from the proccedings website: `python download_iclr_metadata_2015.py`
    - For the year 2016, from the proccedings website: `python download_iclr_metadata_2016.py`
2. Download PDFs:
    - 2013-2016, from arxiv: `python download_iclr_papers_2013-2016.py`
    - 2017-2025, from OpenReview: `python download_iclr_papers.py --username=<OPENREVIEW USERNAME> --password=<OPENREVIEW PASSWORD>`
3. Separate papers accepted to the main conference from the rest:
    - 2013-2014: using manually-curated lists of accepted titles: `python separate_accepted_iclr_2013_2014.py`
    - 2015-2025: using information in the downloaded pdfs: `python separate_accepted_iclr.py`
4.  Parse pdf files to extract affiliations, separately for each year. Example: `python parse_pdfs.py --conf=iclr --year=2024`
5. Compute statistics over all years: `python analyse_affiliations.py --conf=iclr`

#### ICLR processing notes

1. Information about papers at ICLR 2015-2016 is not available through OpenReview API
2. Papers from 2013-2016 are not on OpenReview, they are only on arxiv.
3. For some years, OpenReview API returns all the submitted papers, for some years, it's only accepted papers. Therefore, additional step is needed to separate the main conference accepted papers from others.
4. Other specifics of 2013-2014:
    * Official proceedings website 2013:  'https://iclr.cc/archive/2013/conference-proceedings.html'. This was used to create the file `titles_iclr_2013.txt`
    * Official proceedings website 2014:  'https://iclr.cc/archive/2014/conference-proceedings/' This was used to create the file `titles_iclr_2014.txt`
    * In 2014 the title of one of the papers on [openreview](https://openreview.net/group?id=ICLR.cc/2014/conference) was changed from "Multilingual Distributed Representations without Word Alignment" to "A Simple Model for Learning Multilingual Compositional Semantics".[The pdf](https://arxiv.org/pdf/1312.6173) and the conference [proceedings website](https://iclr.cc/archive/2014/conference-proceedings/) have the old title.


### Plot the figure
Run `python plot_figure.py`

