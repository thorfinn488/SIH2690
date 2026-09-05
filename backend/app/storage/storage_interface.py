from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def read_file(self, file_url: str) -> bytes:
        """
        Reads a previously stored file.
        """
        pass

    @abstractmethod
    def save_file(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """
        Saves file and returns accessibility URL or relative storage path.
        """
        pass

    @abstractmethod
    def delete_file(self, file_url: str) -> bool:
        """
        Deletes file from storage.
        """
        pass
