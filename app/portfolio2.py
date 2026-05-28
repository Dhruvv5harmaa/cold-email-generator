import uuid
from pathlib import Path

import chromadb
import pandas as pd

class Portfolio:

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parent

        file_path = BASE_DIR / "resource" / "my_portfolio.csv"

        self.data = pd.read_csv(file_path)

        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.chroma_client.get_or_create_collection(
            name="portfolio"
        )

    def load_portfolio(self):

        try:

            if self.collection.count() > 0:
                return

            for _, row in self.data.iterrows():

                techstack = str(row["Techstack"]).strip()

                links = str(row["Links"]).strip()

                if not techstack or not links:
                    continue

                self.collection.add(
                    documents=[techstack],
                    metadatas=[{"links": links}],
                    ids=[str(uuid.uuid4())]
                )

        except Exception as e:
            raise Exception(f"Portfolio loading failed: {str(e)}")

    def query_links(self, skills, n_results=2):

        try:

            if not skills:
                return []

            results = self.collection.query(
                query_texts=skills,
                n_results=n_results
            )

            metadatas = results.get("metadatas", [])

            links = []

            for metadata_group in metadatas:
                for item in metadata_group:
                    if "links" in item:
                        links.append(item["links"])

            return list(set(links))

        except Exception as e:
            raise Exception(f"Portfolio query failed: {str(e)}")

