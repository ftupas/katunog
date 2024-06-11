from katunog.api import (
    InstrumentById,
    InstrumentDescriptions,
    InstrumentList,
    InstrumentLocation,
    InstrumentMediaFiles,
    ProvinceList,
    RegionAndIslandList,
)

if __name__ == "__main__":
    instrument_list = InstrumentList(verify=False).get_data(page=1, limit=1)
    print(instrument_list)

    instrument_location = InstrumentLocation(verify=False).get_data(page=1, limit=1)
    print(instrument_location)

    instrument_descriptions = InstrumentDescriptions(verify=False).get_data(page=1, limit=1)
    print(instrument_descriptions)

    instrument_media_files = InstrumentMediaFiles(verify=False).get_data(page=1, limit=1)
    print(instrument_media_files)

    instrument_by_id = InstrumentById(verify=False).get_data(instrument_id="SW5zdHJ1bWVudFR5cGU6MjY1MA==")
    print(instrument_by_id)

    region_and_island_list = RegionAndIslandList(verify=False).get_data()
    print(region_and_island_list)

    province_list = ProvinceList(verify=False).get_data()
    print(province_list)
