import os
import pandas as pd

class Exporter:
    """Exports data to physical files for the client."""
    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def to_excel(self, df: pd.DataFrame, name: str):
        path = os.path.join(self.export_dir, f"{name}.xlsx")
        df.to_excel(path, index=False)
        return path