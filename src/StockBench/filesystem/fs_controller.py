import os
from pathlib import Path


class FSController:
    FIGURES_PATH = Path('figures')

    @staticmethod
    def remove_temp_figures():
        # any file that does not have 'temp' in it is considered persistent and should be left alone

        # remove all top-level temp files in any top-level folder within the temp dir
        for item in FSController.FIGURES_PATH.glob('*'):
            if item.is_file():
                if 'temp' in item.name:
                    try:
                        item.unlink()
                    except (FileNotFoundError, PermissionError):
                        # h2h will both try to clear the temp folder as separate threads, this prevents race conditions
                        # from throwing errors, the first one deletes the file and that's all we need
                        continue

    @staticmethod
    def build_figures_dir_if_not_present():
        # make the directories if they don't already exist
        os.makedirs(FSController.FIGURES_PATH, exist_ok=True)
