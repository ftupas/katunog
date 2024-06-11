from abc import ABC, abstractmethod
import os
from typing import Any, Dict

import requests


class KatunogAPI(ABC):
    """Base class for Katunog API.
    This class is an abstract class that defines the basic structure of the API.
    """

    BASE_URL = "https://katunog.asti.dost.gov.ph"
    API_URL = f"{BASE_URL}/api/"
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, verify: bool = True):
        self.verify = verify

    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass

    def _post_request(self, query: str) -> Dict[Any, Any]:
        response = requests.post(self.API_URL, headers=self.HEADERS, json={"query": query}, verify=self.verify)
        return response.json()


class InstrumentList(KatunogAPI):
    """Get the list of musical instrument"""

    def get_data(self, page: int = 1, limit: int = 10, filter: str = "katunog"):
        query = f"""
        {{
            instruments(page: {page}, limit: {limit}, filter: "{filter}") {{
                page, pages, hasNext, hasPrev, objects {{
                    id,
                    controlNumber,
                    localName,
                    englishName,
                    alternateName,
                    thumbnail,
                    province {{ name }},
                    city {{ name }},
                    ethnolinguistic {{ name }},
                    hornbostel {{ name }},
                    length,
                    width,
                    height,
                    dimensionUnit,
                    diameter,
                    diameterUnit,
                    english {{
                        generalDescription,
                        materialAndMake,
                        playingParts,
                        otherDetails
                    }},
                    filipino {{
                        generalDescription,
                        materialAndMake,
                        playingParts,
                        otherDetails
                    }},
                    lastUpdated,
                    mediaUploadOngoing,
                    isReported,
                    fileSet {{
                        edges {{
                            node {{
                                name,
                                size,
                                caption,
                                fileType,
                                isPublic,
                                uploadDone,
                                path,
                                isBackground,
                                number
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._post_request(query)


class InstrumentLocation(KatunogAPI):
    """Get the location of instrument like island, region, province, city."""

    def get_data(self, page: int = 1, limit: int = 10):
        query = f"""
        {{
            instruments(page: {page}, limit: {limit}) {{
                page,
                pages,
                hasNext,
                hasPrev,
                objects {{
                    id,
                    province {{
                        name,
                        region {{
                            name,
                            island {{ name }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._post_request(query)


class InstrumentDescriptions(KatunogAPI):
    """Get the description of musical instrument in English and Filipino"""

    def get_data(self, page: int = 1, limit: int = 10):
        query = f"""
        {{
            instruments(page: {page}, limit: {limit}) {{
                page,
                pages,
                hasNext,
                hasPrev,
                objects {{
                    id,
                    english {{
                        generalDescription,
                        materialAndMake,
                        playingParts,
                        otherDetails
                    }},
                    filipino {{
                        generalDescription,
                        materialAndMake,
                        playingParts,
                        otherDetails
                    }}
                }}
            }}
        }}
        """
        return self._post_request(query)


class InstrumentMediaFiles(KatunogAPI):
    """Get the available files of the instrument like images, audios and videos"""

    def get_data(self, page: int = 1, limit: int = 10):
        query = f"""
        {{
            instruments(page: {page}, limit: {limit}) {{
                page,
                pages,
                hasNext,
                hasPrev,
                objects {{
                    id,
                    localName,
                    fileSet {{
                        edges {{
                            node {{
                                name,
                                size,
                                caption,
                                fileType,
                                isPublic,
                                uploadDone,
                                path,
                                isBackground,
                                number
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._post_request(query)

    def download_files(self, page: int = 1, limit: int = 10, folder: str = "downloads", file_type: str = ""):
        # Ensure the folder exists
        os.makedirs(folder, exist_ok=True)

        data = self.get_data(page, limit)
        instruments = data.get("data", {}).get("instruments", {}).get("objects", [])

        for instrument in instruments:
            file_set = instrument.get("fileSet", {}).get("edges", [])

            for file_info in file_set:
                node = file_info.get("node", {})
                file_name = node.get("name")
                file_path = node.get("path")

                # Filter by file type if specified
                if file_type and not file_name.endswith(file_type):
                    continue

                # Construct the full URL for the file
                file_url = f"{self.BASE_URL}/api/{file_path}"

                # Download the file
                response = requests.get(file_url, stream=True, verify=self.verify)
                if response.status_code == 200:
                    file_full_path = os.path.join(folder, file_name)
                    with open(file_full_path, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"Downloaded {file_name} to {file_full_path}")
                else:
                    print(f"Failed to download {file_name}")


class InstrumentById(KatunogAPI):
    """Get the specific instrument"""

    def get_data(self, instrument_id: str):
        query = f"""
        {{
            instrument(id: "{instrument_id}") {{
                controlNumber,
                localName,
                englishName,
                alternateName,
                fileSet {{
                    edges {{
                        node {{
                            name,
                            path
                        }}
                    }}
                }}
            }}
        }}
        """
        return self._post_request(query)


class RegionAndIslandList(KatunogAPI):
    """This endpoint allows users to get the list of the region and island"""

    def get_data(self):
        query = """
        {
            regions {
                name
                island {
                    name
                }
            }
        }
        """
        return self._post_request(query)


class ProvinceList(KatunogAPI):
    """This endpoint will show all the province available in database"""

    def get_data(self):
        query = """
        {
            provinces {
                id,
                name
            }
        }
        """
        return self._post_request(query)
