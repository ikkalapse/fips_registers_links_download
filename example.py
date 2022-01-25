import requests

from fips_registers_links_download.fips_registers_links_download import FipsRegistersLinksDownloader
from datetime import datetime
import os

for ois_type in 'DB TIMS EVM RUPM RUDE RUPAT'.split():

    print(ois_type)

    start_time = datetime.now()

    downloader = FipsRegistersLinksDownloader(ois_type, filename_suffix='') #, project_dir='...')

    downloader.download_links()

    end_time = datetime.now()

    with open(os.path.join(downloader.project_dir, "stat-" + ois_type + ".txt"), "w") as file:

        file.write("Start NodeId:" + downloader.start_nodeid + "\n")
        file.write("Total links: " + str(len(downloader.links)) + "\n")
        file.write("Duration: {}".format(end_time - start_time) + "\n")
