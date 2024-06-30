import csv
import asyncio
import aiohttp
from dataclasses import dataclass, fields
from typing import List, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import config


@dataclass
class Job:
    title: str
    description: str
    experience: str
    level: str
    skills: List[str]


JOB_FIELDS = [field.name for field in fields(Job)]

LEVEL_MAPPING = {
    "junior": "Junior",
    "middle": "Middle",
    "senior": "Senior"
}


class JobScraper:
    def __init__(self, base_url: str, filename: str):
        self.base_url = base_url
        self.filename = filename
        self.jobs = []

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    async def parse_jobs_on_page(self, session: aiohttp.ClientSession, url: str):
        page_content = await self.fetch_page(session, url)
        soup = BeautifulSoup(page_content, 'html.parser')
        job_elements = soup.select("div.card-hover")

        for job_element in job_elements:
            title = self.get_title(job_element)
            description = self.get_description(job_element)
            experience, level = self.get_experience_and_level(description)
            job_url = job_element.find('a')['href']
            job_url = urljoin(self.base_url, job_url)
            skills = await self.get_skills(session, job_url)
            self.jobs.append(Job(title, description, experience, level, skills))

        next_page = self.get_next_page(soup)
        return next_page

    def get_title(self, job_element) -> str:
        title_elem = job_element.select_one("h2.my-0 a")
        return title_elem.text if title_elem else "No title"

    def get_description(self, job_element) -> str:
        description_elem = job_element.select_one("p.ellipsis.ellipsis-line.ellipsis-line-3.text-default-7.mb-0")
        return description_elem.text if description_elem else "No description"

    def get_experience_and_level(self, description: str) -> Tuple[str, str]:
        sentences = description.lower().split('.')
        experience_years = []

        for sentence in sentences:
            if 'experience' in sentence or 'досвід' in sentence:
                words = sentence.split()
                for i, word in enumerate(words):
                    if word.isdigit():
                        if i + 1 < len(words) and words[i + 1] in ['years', 'років', 'рік', 'річний', 'роки', 'року']:
                            experience_years.append(int(word))

        if experience_years:
            max_experience = max(experience_years)
            experience = f"{max_experience} years of experience"
            level = self.categorize_experience(max_experience)
        else:
            experience = "Not specified"
            level = "Not specified"
        return experience, level

    def categorize_experience(self, years: int) -> str:
        if years < 2:
            return "Junior"
        elif 2 <= years < 5:
            return "Middle"
        else:
            return "Senior"

    async def get_skills(self, session: aiohttp.ClientSession, job_url: str) -> List[str]:
        page_content = await self.fetch_page(session, job_url)
        soup = BeautifulSoup(page_content, 'html.parser')
        skill_elements = soup.select("span.ellipsis")
        skills = [skill_elem.text for skill_elem in skill_elements]
        return skills if skills else ["Not specified"]

    def get_next_page(self, soup) -> str | None:
        next_button = soup.select_one("li[class='no-style add-left-default'] a")
        if next_button and 'disabled' not in next_button.get('class', []):
            next_page_url = next_button['href']
            return urljoin(self.base_url, next_page_url)
        return None

    async def scrape_jobs(self):
        async with aiohttp.ClientSession() as session:
            next_page = self.base_url
            while next_page:
                next_page = await self.parse_jobs_on_page(session, next_page)

    def write_to_csv(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=JOB_FIELDS)
            writer.writeheader()
            for job in self.jobs:
                writer.writerow({
                    "title": job.title,
                    "description": job.description,
                    "experience": job.experience,
                    "level": job.level,
                    "skills": ", ".join(job.skills) if job.skills else "Not specified"
                })

    async def get_all_jobs(self):
        await self.scrape_jobs()
        self.write_to_csv()
        print(f"Scraped {len(self.jobs)} jobs.")


if __name__ == "__main__":
    scraper = JobScraper(base_url=config.BASE_URL, filename=config.FILENAME)
    asyncio.run(scraper.get_all_jobs())
