import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import config


class JobAnalyzer:
    def __init__(self, filename: str):
        self.filename = filename
        self.df = self.load_data()

    def load_data(self):
        return pd.read_csv(self.filename)

    def analyze_skills(self, df=None):
        if df is None:
            df = self.df
        all_skills = []
        for skill_list in df['skills']:
            if isinstance(skill_list, str):
                skills = [skill.strip() for skill in skill_list.split(',')]
                all_skills.extend(skills)
        return Counter(all_skills).most_common(20)

    def plot_skills(self, counter, title='Most Demanded Skills'):
        labels, values = zip(*counter)
        plt.figure(figsize=(10, 8))
        plt.barh(labels, values)
        plt.xlabel('Frequency')
        plt.title(title)
        plt.gca().invert_yaxis()
        plt.show()

    def analyze_and_plot_by_level(self, level):
        df_level = self.df[self.df['level'] == level]
        skill_counter = self.analyze_skills(df_level)
        self.plot_skills(skill_counter, title=f'Most Demanded Skills for {level}')

    def analyze(self):
        skill_counter = self.analyze_skills()
        self.plot_skills(skill_counter)

        for level in ['Junior', 'Middle', 'Senior']:
            self.analyze_and_plot_by_level(level)


if __name__ == '__main__':
    analyzer = JobAnalyzer(filename=config.FILENAME)
    analyzer.analyze()
