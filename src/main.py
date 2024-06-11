import asyncio
import logging

from katunog.api import (
    InstrumentById,
    InstrumentDescriptions,
    InstrumentList,
    InstrumentLocation,
    InstrumentMediaFiles,
    ProvinceList,
    RegionAndIslandList,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    try:
        instrument_list = await InstrumentList(ssl=False).get_data(page=1, limit=1)
        logger.info(f"Instrument List: {instrument_list}")

        instrument_location = await InstrumentLocation(ssl=False).get_data(page=1, limit=1)
        logger.info(f"Instrument Location: {instrument_location}")

        instrument_descriptions = await InstrumentDescriptions(ssl=False).get_data(page=1, limit=1)
        logger.info(f"Instrument Descriptions: {instrument_descriptions}")

        instrument_media_files = await InstrumentMediaFiles(ssl=False).get_data(page=1, limit=1)
        logger.info(f"Instrument Media Files: {instrument_media_files}")

        instrument_by_id = await InstrumentById(ssl=False).get_data(instrument_id="SW5zdHJ1bWVudFR5cGU6MjY1MA==")
        logger.info(f"Instrument By ID: {instrument_by_id}")

        region_and_island_list = await RegionAndIslandList(ssl=False).get_data()
        logger.info(f"Region and Island List: {region_and_island_list}")

        province_list = await ProvinceList(ssl=False).get_data()
        logger.info(f"Province List: {province_list}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    # Download samples
    await InstrumentMediaFiles(ssl=False).download_files()


if __name__ == "__main__":
    asyncio.run(main())
