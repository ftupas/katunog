import asyncio

from katunog.api import (
    InstrumentById,
    InstrumentDescriptions,
    InstrumentList,
    InstrumentLocation,
    InstrumentMediaFiles,
    ProvinceList,
    RegionAndIslandList,
)


async def main():
    instrument_list = await InstrumentList(ssl=False).get_data(page=1, limit=1)
    print(instrument_list)

    instrument_location = await InstrumentLocation(ssl=False).get_data(page=1, limit=1)
    print(instrument_location)

    instrument_descriptions = await InstrumentDescriptions(ssl=False).get_data(page=1, limit=1)
    print(instrument_descriptions)

    instrument_media_files = await InstrumentMediaFiles(ssl=False).get_data(page=1, limit=1)
    print(instrument_media_files)

    instrument_by_id = await InstrumentById(ssl=False).get_data(instrument_id="SW5zdHJ1bWVudFR5cGU6MjY1MA==")
    print(instrument_by_id)

    region_and_island_list = await RegionAndIslandList(ssl=False).get_data()
    print(region_and_island_list)

    province_list = await ProvinceList(ssl=False).get_data()
    print(province_list)


if __name__ == "__main__":
    asyncio.run(main())
