import os
from os import path

import pandas as pd


class Results(object):

    def __init__(self, file_path):

        self.columns = [
            "File name",
            "RGC count",
            "Area (mm^2)",
            "Density (cells/mm^2)"
        ]
        
        self.results_df = pd.DataFrame(columns=self.columns)

        self.file_path = file_path

        self.ext = path.splitext(file_path)[-1]
    

    def save_results(self):
        
        try:
            if self.ext == ".csv":
                self.results_df.to_csv(self.file_path)
            elif self.ext == ".xlsx":
                self.results_df.to_excel(self.file_path)
        except PermissionError:
            print(f"Unable to save the result file!\nThe file is probably opened in another application!")

            n = 1
            alternative_path = path.splitext(self.file_path)[0]
            alternative_path = f"{alternative_path}-{n}.{self.ext}"

            while path.exists(alternative_path):
                n += 1
                alternative_path = f"{alternative_path}-{n}.{self.ext}"
            
            self.file_path = alternative_path


    def add_results(self, retina):

        data = [
            retina.filename,
            retina.count,
            retina.area,
            retina.density
        ]

        data_df = pd.DataFrame([data], columns=self.columns)

        self.results_df = pd.concat([self.results_df, data_df], ignore_index=True)

        self.save_results()
        