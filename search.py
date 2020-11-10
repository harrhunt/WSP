from googleapiclient.discovery import build
from credentials import *


class Google:
    api_key = GOOGLE_API_KEY
    cse_id = CUSTOM_SEARCH_ENGINE_ID

    @classmethod
    def google_search(cls, query, **kwargs):
        service = build("customsearch", "v1", developerKey=cls.api_key)
        results = service.cse().list(q=query, cx=cls.cse_id, **kwargs).execute()
        return results

    @classmethod
    def get_hits(cls, query, **kwargs):
        results = cls.google_search(query, **kwargs)
        return int(results["queries"]["request"][0]["totalResults"])


if __name__ == '__main__':
    hits = Google.get_hits("plane")
    print(hits)
