from __future__ import annotations
from ..ports.runtime_catalog import RuntimeCatalogPort
class ListCapabilities:
    def __init__(self,catalog:RuntimeCatalogPort)->None: self.catalog=catalog
    def execute(self)->dict:
        return {d.runtime_set_id:d.capability_manifest.get('languages',{}) for d in self.catalog.list_runtime_sets()}
