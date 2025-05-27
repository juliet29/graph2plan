from ..dual.interfaces import Domains
from ..constants import OUTPUTS_PATH

def merged_domains_to_floorplan(domains: Domains):
    domains.write_floorplan(OUTPUTS_PATH) # TODO how to test this? 