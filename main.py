import argparse
import asyncio
from web_scraping import JobScraper
from data_analysis import JobAnalyzer
import config


def main(scrape, analyze):
    if scrape:
        print("Scraping job data")
        scraper = JobScraper(base_url=config.BASE_URL, filename=config.FILENAME)
        asyncio.run(scraper.get_all_jobs())
        print("Job data saved to jobs.csv")

    if analyze:
        print("Analyzing job data")
        analyzer = JobAnalyzer(filename=config.FILENAME)
        analyzer.analyze()
        print("Analysis complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and analyze job data")
    parser.add_argument('--scrape', action='store_true', help="Scrape job listings from Work.ua")
    parser.add_argument('--analyze', action='store_true', help="Analyze the scraped job data")

    args = parser.parse_args()
    main(scrape=args.scrape, analyze=args.analyze)
