__all__ = ['QdrantServer', 'get_qdrant_server']

import logging
import subprocess
import time

import config

logger = logging.getLogger(__name__)


class QdrantServer:
    DEFAULT_URL = config.QDRANT_URL
    CONTAINER_NAME = 'chat_analyzer_qdrant'

    def __init__(
        self,
        url: str = DEFAULT_URL,
        docker_image: str = 'qdrant/qdrant',
        volume_path: str = config.QDRANT_VOLUME_PATH,
    ):
        self.url = url
        self.docker_image = docker_image
        self.volume_path = volume_path
        self._is_running = False

    def is_running(self):
        try:
            result = subprocess.run(
                [
                    'sudo',
                    'docker',
                    'inspect',
                    '--format',
                    '{{.State.Running}}',
                    self.CONTAINER_NAME,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() == 'true'
        except Exception as e:
            logger.exception(f'Failed to execute docker: {e}')
            return False

    def _remove_container_if_exists(self):
        logger.info(f'Checking container {self.CONTAINER_NAME}...')
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '-q', '--filter', f'name={self.CONTAINER_NAME}'],
            capture_output=True,
            text=True,
            check=False,
        )

        container_ids = result.stdout.strip()
        if container_ids:
            logger.debug('Existing container found, removing...')
            rm_result = subprocess.run(
                ['sudo', 'docker', 'rm', '-f', self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                check=False,
            )
            if rm_result.returncode == 0:
                logger.info(f'Container "{self.CONTAINER_NAME}" removed.')
            else:
                logger.warning(f'Failed to remove container: {rm_result.stderr.strip()}')

        return container_ids

    def start(self, timeout: int = 30):
        logger.info('Starting Qdrant server (Docker)...')

        # TODO: Убрать удаление контейнера
        self._remove_container_if_exists()

        time.sleep(1)

        if self.is_running():
            logger.debug('Container already running.')
            self._is_running = True
            return True

        cmd = (
            ['sudo', 'docker', 'run', '-d']
            + ['-p', '6333:6333']
            + ['-p', '6334:6334']
            + ['--name', self.CONTAINER_NAME]
            + ['-v', f'{self.volume_path}:/qdrant/storage:z']
            + [self.docker_image]
        )

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f'Docker start error:\n{result.stderr.strip()}')
            return False

        for _ in range(timeout):
            time.sleep(1)
            if self.is_running():
                logger.info('Qdrant server started successfully!')
                self._is_running = True
                time.sleep(5)
                return True

        logger.error(f'Qdrant failed to start within {timeout} sec.')
        return False

    def stop(self, force: bool = True):
        logger.info('Stopping Qdrant server...')

        timeout = '2' if force else '30'
        cmd = ['sudo', 'docker', 'stop', '-t', timeout, self.CONTAINER_NAME]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            self._is_running = False
            logger.debug('Container stopped.')
            return True

        logger.error(f'Stop error:\n{result.stderr.strip()}')
        return False

    def restart(self, timeout: int = 30):
        self.stop(force=False)
        time.sleep(2)
        return self.start(timeout=timeout)

    def _get_container_ids(self):
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '-q', '--filter', f'name={self.CONTAINER_NAME}'],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()


def get_qdrant_server(url: str = config.QDRANT_URL, volume_path: str = config.QDRANT_VOLUME_PATH):
    return QdrantServer(url=url, volume_path=volume_path)


if __name__ == '__main__':
    server = QdrantServer()
    logger.info(f'Current status: {"Running" if server.is_running() else "Stopped"}')
