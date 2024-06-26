from abc import ABC, abstractmethod
import asyncio
import logging
import os
import re
from typing import Any, Dict, Union

import aiohttp
import pandas as pd


class KatunogAPI(ABC):
    """Base class for Katunog API.
    This class is an abstract class that defines the basic structure of the API.
    """

    BASE_URL = "https://katunog.asti.dost.gov.ph"
    API_URL = f"{BASE_URL}/api/"
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, ssl: bool = True):
        self.ssl = ssl

    @abstractmethod
    async def get_data(self, *args, **kwargs):
        pass

    async def _post_request(self, query: str) -> Dict[Any, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.API_URL, headers=self.HEADERS, json={"query": query}, ssl=self.ssl
            ) as response:
                return await response.json()


class InstrumentList(KatunogAPI):
    """Get the list of musical instrument"""

    async def get_data(self, page: int = 1, limit: int = 10, filter: str = "katunog"):
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
        return await self._post_request(query)

    def to_dataframe(self, instrument_data: Dict[Any, Any]):
        items = instrument_data.get("data", {}).get("instruments", {}).get("objects", [])
        instruments_list = []

        for item in items:
            city = item.get("city", {})
            province = item.get("province", {})
            english = item.get("english", {})
            hornbostel = item.get("hornbostel", {})

            city_name = city.get("name", "") if city else ""
            province_name = province.get("name", "") if province else ""
            material_and_make = english.get("materialAndMake", "") if english else ""
            hornbostel_name = hornbostel.get("name", "") if hornbostel else ""

            instrument = {
                "Instrument": item.get("localName", ""),
                "Ethnolinguistic Group": item.get("ethnolinguistic", {}).get("name", ""),
                "Location": f"{city_name}, {province_name}",
                "English Name": item.get("englishName", ""),
                "Materials and Make Classification": material_and_make,
                "Hornbostel": hornbostel_name,
            }
            instruments_list.append(instrument)

        df = pd.DataFrame(
            instruments_list,
            columns=[
                "Instrument",
                "Ethnolinguistic Group",
                "Location",
                "English Name",
                "Materials and Make Classification",
                "Horbostel",
            ],
        )

        return df


class InstrumentLocation(KatunogAPI):
    """Get the location of instrument like island, region, province, city."""

    async def get_data(self, page: int = 1, limit: int = 10):
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
        return await self._post_request(query)


class InstrumentDescriptions(KatunogAPI):
    """Get the description of musical instrument in English and Filipino"""

    async def get_data(self, page: int = 1, limit: int = 10):
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
        return await self._post_request(query)


class InstrumentMediaFiles(KatunogAPI):
    """Get the available files of the instrument like images, audios and videos"""

    async def get_data(self, page: int = 1, limit: int = 10):
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
        return await self._post_request(query)

    async def download_files(
        self, page: int = 1, limit: int = 10, folder: str = "downloads", file_type: str = "audio", num_threads: int = 5
    ):
        # Ensure the folder exists
        os.makedirs(folder, exist_ok=True)

        # Get existing list of instruments in the folder
        existing_files = os.listdir(folder)

        data = await self.get_data(page, limit)
        instruments = data.get("data", {}).get("instruments", {}).get("objects", [])

        processed_instruments = set()

        async with aiohttp.ClientSession() as session:
            tasks = []
            for instrument in instruments:
                file_set = instrument.get("fileSet", {}).get("edges", [])
                instrument_id = instrument.get("id")
                instrument_name = (
                    (await InstrumentById(ssl=self.ssl).get_data(instrument_id))
                    .get("data", {})
                    .get("instrument", {})
                    .get("localName")
                )

                for file_info in file_set:
                    node = file_info.get("node", {})
                    file_path = node.get("path")

                    # Extract instrument download ID from the file path
                    instrument_download_id = self.extract_instrument_download_id(file_path)
                    if not instrument_download_id:
                        logging.error(f"Failed to extract instrument ID from path: {file_path}")
                        continue

                    # Skip if this instrument has already been processed
                    if instrument_download_id in processed_instruments:
                        continue
                    logging.info(f"Extracted ID: {instrument_download_id} for {instrument_name}")
                    processed_instruments.add(instrument_download_id)

                    download_url = f"{self.BASE_URL}/instruments/download_all_files?instrument_id={instrument_download_id}&file_type={file_type}"  # noqa: E501
                    logging.info(f"Downloading {instrument_name} from {download_url}")

                    # Create a task for downloading the file
                    file_name = f"{instrument_name}.zip"
                    exists = file_name in existing_files
                    if not exists:
                        tasks.append(
                            self.download_file(session, download_url, os.path.join(folder, file_name), instrument_name)
                        )
                    else:
                        logging.info(f"{instrument_name} already exists in {folder}")

                    # Limit the number of concurrent tasks
                    if len(tasks) >= num_threads:
                        await asyncio.gather(*tasks)
                        tasks = []

            # Run any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)

    async def download_file(self, session: aiohttp.ClientSession, url: str, file_path: str, instrument_name: str):
        async with session.get(url, ssl=self.ssl) as response:
            if response.status == 200:
                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(1024):
                        f.write(chunk)
                logging.info(f"Downloaded {instrument_name} to {file_path}")
            else:
                logging.error(f"Failed to download {instrument_name} from {url}")

    def extract_instrument_download_id(self, path: str) -> Union[str, None]:
        instrument = re.compile(r"PIISD0(\d+)/")
        match = instrument.search(path)
        if match:
            return match.group(1)
        return None


class InstrumentById(KatunogAPI):
    """Get the specific instrument"""

    async def get_data(self, instrument_id: str):
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
        return await self._post_request(query)


class RegionAndIslandList(KatunogAPI):
    """This endpoint allows users to get the list of the region and island"""

    async def get_data(self):
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
        return await self._post_request(query)


class ProvinceList(KatunogAPI):
    """This endpoint will show all the province available in database"""

    async def get_data(self):
        query = """
        {
            provinces {
                id,
                name
            }
        }
        """
        return await self._post_request(query)
