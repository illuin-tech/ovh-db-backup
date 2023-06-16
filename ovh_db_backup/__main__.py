import logging
import os
import time
from dataclasses import dataclass

import ovh
import requests


@dataclass
class App:
    logger = logging.getLogger(__name__)
    service_name: str = None
    database_name: str = None
    max_retries: int = 60
    sleep_time: int = 6
    client: ovh.Client = None

    def wait_until_new_backup(self, latest_backup: int, retries: int = 0) -> int:
        backups = self.client.get(
            f"/hosting/privateDatabase/{self.service_name}/database/{self.database_name}/dump"
        )
        new_latest_backup = max(backups)
        if new_latest_backup == latest_backup:
            if retries > self.max_retries:
                self.logger.error(
                    f"Backup was not completed in time. Latest backup : {latest_backup}"
                )
                raise Exception()
            self.logger.debug(
                f"Latest backup has not changed, waiting {App.sleep_time}s more. Retry : {retries}"
            )
            time.sleep(self.sleep_time)
            return self.wait_until_new_backup(latest_backup, retries + 1)
        return new_latest_backup

    def trigger_backup(self):
        backups = self.client.get(
            f"/hosting/privateDatabase/{self.service_name}/database/{self.database_name}/dump"
        )
        self.logger.debug(
            f"Retrieved existing backups : {backups!r} / latest : {max(backups)}"
        )
        self.logger.info(
            f"Creating a new backup for {self.service_name}/{self.database_name}"
        )
        task = self.client.post(
            f"/hosting/privateDatabase/{self.service_name}/database/{self.database_name}/dump"
        )
        self.logger.debug(f"New backup task details : {task!r}")
        self.logger.info(f"Waiting until backup is finished")
        new_backup = self.wait_until_new_backup(max(backups))
        backup = self.client.get(
            f"/hosting/privateDatabase/{self.service_name}/database/{self.database_name}/dump/{new_backup}"
        )
        self.logger.debug(f"Backup details : {backup!r}")
        req = requests.head(backup["url"])
        if req.status_code != 200:
            self.logger.error(f"Backup not available at url {backup['url']}")
            raise Exception()
        self.logger.info(f"Backup {backup['id']} is finished")


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.INFO))
    app = App(
        client=ovh.Client(endpoint=os.getenv("OVH_ENDPOINT", "ovh-eu")),
        service_name=os.getenv("BACKUP_SERVICE_NAME"),
        database_name=os.getenv("BACKUP_DATABASE_NAME"),
    )
    app.trigger_backup()
