from dataclasses import dataclass
from pathlib import Path

from igi2cs.file_utils import FileBuffer
from igi2cs.mtp import MTPFile
from igi2cs.res import ResArchive


@dataclass
class MPTRecord:
    path: Path
    mtp: MTPFile

@dataclass
class ResRecord:
    path: Path
    res: ResArchive


class ContentManager:

    def __init__(self, base_path: Path):
        self._base_path = base_path
        self._mpt_records: list[MPTRecord] = self.scan_mpt()
        self._res_records: list[ResRecord] = self.scan_res()

    def scan_mpt(self) -> list[MPTRecord]:
        mtps = []
        for mtp_path in self._base_path.rglob("*.mtp"):
            with FileBuffer(mtp_path) as f:
                mtp = MTPFile(f)
                mtps.append(MPTRecord(mtp_path.parent, mtp))
        return mtps

    def scan_res(self)->list[ResRecord]:
        ress = []
        for res_path in self._base_path.rglob("*.res"):
            with FileBuffer(res_path) as f:
                res = ResArchive(f)
                ress.append(ResRecord(res_path, res))
        return ress

    def get_texture_names(self, model_path: Path):
        model_name = model_path.stem
        parent = model_path.parent
        for record in self._mpt_records:
            if parent.is_relative_to(record.path):
                return record.mtp.get_texture_names(model_name)
