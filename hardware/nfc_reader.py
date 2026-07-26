"""Ansteuerung des NFC-Lesegeräts (z.B. PN532/MFRC522) im Statuen-Fach."""


class NFCReader:
    def __init__(self, port):
        self.port = port

    def read_uid(self):
        """Gibt die UID der aufgelegten Statue zurück, oder None wenn keine erkannt wird."""
        raise NotImplementedError
