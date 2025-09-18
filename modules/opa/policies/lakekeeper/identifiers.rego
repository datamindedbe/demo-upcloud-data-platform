package lakekeeper

import data.configuration
import data.lakekeeper

# Translate a warehouse name to a warehouse ID.
# Cache the result for 1 hour to avoid repeated calls to the Lakekeeper API.
warehouse_id_for_name(lakekeeper_id, warehouse_name) := warehouse_id if {
    this := lakekeeper.lakekeeper_by_id[lakekeeper_id]
    url := concat("/", [this.url, "management/v1/warehouse"])
    print("get warehouse id for name")
    body := http.send({
        "method": "GET",  
        "url": url,
        "force_cache": true,
        "force_cache_duration_seconds": 3600,
        "caching_mode": "deserialized",
    }).body
    lakekeeper_warehouse := body.warehouses[_]
    warehouse_name == lakekeeper_warehouse.name
    warehouse_id := lakekeeper_warehouse.id
}
