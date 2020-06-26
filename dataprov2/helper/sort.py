from typing import Sequence, Set

from prov.model import ProvDocument


def sort(seq: Sequence[ProvDocument]) -> Sequence[ProvDocument]:
    seen: Set[ProvDocument] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
