"""
Sistema de observação de arquivos para hot reload.
"""

import logging
import os
from pathlib import Path
from typing import Callable, Dict, List, Set, Union

from PySide6.QtCore import QObject, Signal
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FileChangeHandler(FileSystemEventHandler):
    """Handler para eventos de modificação de arquivos."""

    def __init__(
        self, callback: Callable[[str], None], file_patterns: Set[str]
    ) -> None:
        """
        Inicializa o handler.

        Args:
            callback: Função a ser chamada quando um arquivo for modificado
            file_patterns: Padrões de arquivos a serem observados (ex: *.py, *.qss)
        """
        super().__init__()
        self.callback = callback
        self.file_patterns = file_patterns
        self._last_modified: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Chamado quando um arquivo é modificado.

        Args:
            event: Evento de modificação
        """
        if not event.is_directory:
            file_path = event.src_path
            # Verifica se o arquivo corresponde aos padrões
            if any(file_path.endswith(pattern) for pattern in self.file_patterns):
                # Evita chamadas duplicadas (alguns sistemas de arquivos geram múltiplos eventos)
                try:
                    current_time = os.path.getmtime(file_path)
                    last_time = self._last_modified.get(file_path, 0)
                    if current_time > last_time + 0.5:  # 500ms de debounce
                        self._last_modified[file_path] = current_time
                        self.logger.debug(f"Arquivo modificado: {file_path}")
                        self.callback(file_path)
                except OSError as e:
                    self.logger.error(f"Erro ao acessar arquivo {file_path}: {e}")


class FileWatcher(QObject):
    """Sistema de observação de arquivos para hot reload."""

    # Sinais
    file_changed = Signal(str)  # Emitido quando um arquivo é modificado

    def __init__(self, watch_dirs: Union[Path, List[Path]]) -> None:
        """
        Inicializa o observador de arquivos.

        Args:
            watch_dirs: A single directory path or list of directory paths to watch.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.observer = Observer()
        self.handlers: List[FileChangeHandler] = []
        self.started = False

        # Converter para lista se for um único diretório
        if isinstance(watch_dirs, (str, Path)):
            watch_dirs = [Path(watch_dirs)]
        else:
            watch_dirs = [Path(d) for d in watch_dirs]

        self.watch_dirs = watch_dirs
        self.logger.debug(f"Diretórios a serem observados: {self.watch_dirs}")

        # Configurar observação dos diretórios
        for directory in self.watch_dirs:
            self.watch_directory(directory)

    def watch_directory(
        self,
        directory: str | Path,
        patterns: Set[str] = {".py", ".qss", ".css"},
    ) -> None:
        """
        Adiciona um diretório para observação.

        Args:
            directory: Caminho do diretório a ser observado
            patterns: Padrões de arquivos a serem observados
        """
        directory = Path(directory)
        if not directory.exists():
            self.logger.warning(f"Diretório não encontrado: {directory}")
            return

        try:
            handler = FileChangeHandler(self.file_changed.emit, patterns)
            self.handlers.append(handler)
            self.observer.schedule(handler, str(directory), recursive=True)
            self.logger.debug(f"Observando diretório: {directory}")
        except Exception as e:
            self.logger.error(
                f"Erro ao configurar observação do diretório {directory}: {e}"
            )

    def start(self) -> None:
        """Inicia a observação de arquivos."""
        if not self.started:
            try:
                self.observer.start()
                self.started = True
                self.logger.info("Sistema de hot reload iniciado")
            except Exception as e:
                self.logger.error(f"Erro ao iniciar observador: {e}")

    def stop(self) -> None:
        """Para a observação de arquivos."""
        if self.started:
            try:
                self.observer.stop()
                self.observer.join()
                self.started = False
                self.logger.info("Sistema de hot reload parado")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar observador: {e}")
