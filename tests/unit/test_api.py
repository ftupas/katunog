from src.katunog.api import (
    InstrumentById,
    InstrumentDescriptions,
    InstrumentList,
    InstrumentLocation,
    InstrumentMediaFiles,
    KatunogAPI,
    ProvinceList,
    RegionAndIslandList,
)
from tests.unit.abstract_function_test_case import AbstractFunctionTestCase


class TestInstrumentAPIBase(AbstractFunctionTestCase):
    def assert_get_data(self, api_instance: KatunogAPI, query: str, *args, **kwargs):
        api_instance.get_data(*args, **kwargs)
        self.mock_post.assert_called_once_with(
            api_instance.API_URL,
            headers=api_instance.HEADERS,
            json={"query": query},
            verify=api_instance.verify,
        )


class TestInstrumentList(TestInstrumentAPIBase):
    def test_get_data(self):
        page = limit = 1
        filter = "katunog"
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
        self.assert_get_data(InstrumentList(), query, page=page, limit=limit, filter=filter)


class TestInstrumentLocation(TestInstrumentAPIBase):
    def test_get_data(self):
        page = limit = 1
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
        self.assert_get_data(InstrumentLocation(), query, page=page, limit=limit)


class TestInstrumentDescriptions(TestInstrumentAPIBase):
    def test_get_data(self):
        page = limit = 1
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
        self.assert_get_data(InstrumentDescriptions(), query, page=page, limit=limit)


class TestInstrumentMediaFiles(TestInstrumentAPIBase):
    def test_get_data(self):
        page = limit = 1
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
        self.assert_get_data(InstrumentMediaFiles(), query, page=page, limit=limit)


class TestInstrumentById(TestInstrumentAPIBase):
    def test_get_data(self):
        instrument_id = "SW5zdHJ1bWVudFR5cGU6MjY1MA=="
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
        self.assert_get_data(InstrumentById(), query, instrument_id=instrument_id)


class TestRegionAndIslandList(TestInstrumentAPIBase):
    def test_get_data(self):
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
        self.assert_get_data(RegionAndIslandList(), query)


class TestProvinceList(TestInstrumentAPIBase):
    def test_get_data(self):
        query = """
        {
            provinces {
                id,
                name
            }
        }
        """
        self.assert_get_data(ProvinceList(), query)
