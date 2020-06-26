import logging

from prov.model import ProvDocument


def deserialize(document: ProvDocument, file: str) -> None:
    try:
        k: ProvDocument = ProvDocument().deserialize(file, format="xml")
        logging.debug(f"Deserializing {file}")
        document.update(k)

    except FileNotFoundError:
        pass
