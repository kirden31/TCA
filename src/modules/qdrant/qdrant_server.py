from pathlib import Path
import subprocess
import time
import logging

logger = logging.getLogger(__name__)

import config


class QdrantServer:
    DEFAULT_URL = config.qdrant_url
    CONTAINER_NAME = 'chat_analyzer_qdrant'

    def __init__(
        self,
        url: str = DEFAULT_URL,
        docker_image: str = 'qdrant/qdrant',
        volume_path: Path = Path.cwd() / 'qdrant_storage',
    ):
        self.url = url
        self.docker_image = docker_image
        self.volume_path = volume_path
        self._is_running = False

    def is_running(self) -> bool:
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
        except Exception:
            return False

    def _remove_container_if_exists(self):
        logger.info(f'Проверка контейнера {self.CONTAINER_NAME}...')
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '-q', '--filter', f'name={self.CONTAINER_NAME}'],
            capture_output=True,
            text=True,
            check=False,
        )

        container_ids = result.stdout.strip()
        if container_ids:
            logger.debug('Найден существующий контейнер, удаляю...')
            rm_result = subprocess.run(
                ['sudo', 'docker', 'rm', '-f', self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                check=False,
            )
            if rm_result.returncode == 0:
                logger.info(f'Контейнер "{self.CONTAINER_NAME}" удалён.')
            else:
                logger.warning(f'Не удалось удалить контейнер: {rm_result.stderr.strip()}')
        return container_ids

    def start(self, timeout: int = 30) -> bool:
        logger.info('Запуск Qdrant сервера (Docker)...')

        self._remove_container_if_exists()

        time.sleep(1)

        if self.is_running():
            logger.debug('Контейнер уже запущен.')
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
            logger.error(f'Ошибка запуска Docker:\n{result.stderr.strip()}')
            return False

        for _ in range(timeout):
            time.sleep(1)
            if self.is_running():
                logger.info('Qdrant сервер успешно запущен!')
                self._is_running = True
                return True

        logger.error(f'Qdrant не запустился в течение {timeout} сек.')
        return False

    def stop(self, force: bool = True) -> bool:
        logger.info('Остановка Qdrant сервера...')

        timeout = '2' if force else '30'
        cmd = ['sudo', 'docker', 'stop', '-t', timeout, self.CONTAINER_NAME]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            self._is_running = False
            logger.debug('Контейнер остановлен.')
            return True

        logger.error(f'Ошибка остановки:\n{result.stderr.strip()}')
        return False

    def restart(self, timeout: int = 30) -> bool:
        self.stop(force=False)
        time.sleep(2)
        return self.start(timeout=timeout)

    def _get_container_ids(self) -> str:
        result = subprocess.run(
            ['sudo', 'docker', 'ps', '-a', '-q', '--filter', f'name={self.CONTAINER_NAME}'],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()


def get_qdrant_server(url: str = config.qdrant_url, volume_path: Path = config.qdrant_volume_path):
    return QdrantServer(url=url, volume_path=volume_path)


if __name__ == '__main__':
    server = QdrantServer()
    logger.info(f'Текущий статус: {'Запущен' if server.is_running() else 'Остановлен'}')
