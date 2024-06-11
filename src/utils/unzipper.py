import logging
import os
import zipfile


class Unzipper:
    def __init__(self, zip_folder: str, output_folder: str):
        self.zip_folder = zip_folder
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def unzip_files(self):
        for file_name in os.listdir(self.zip_folder):
            if file_name.endswith(".zip"):
                zip_path = os.path.join(self.zip_folder, file_name)
                self._unzip_file(zip_path)

    def _unzip_file(self, zip_path: str):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.output_folder)
                logging.info(f"Extracted {zip_path} to {self.output_folder}")
        except zipfile.BadZipFile:
            logging.error(f"Bad zip file: {zip_path}")
        except Exception as e:
            logging.error(f"Failed to unzip {zip_path}: {e}")
