"""STK cross-path sampling plus platform-side directional interference analysis."""
from __future__ import annotations

from .interference import aggregate_downlink, spectral_overlap


def _values(result, name):
    return list(result.DataSets.GetDataSetByName(name).GetValues())


def analyze(root, links, devices, antennas, satellites, time_grid, step, geometry_visible,
            feeder_geometry, object_paths, budget_rows, progress, receiver_masks=None):
    downlinks = [link for link in links if link["direction"] in {"DOWNLINK", "FEEDER_DOWNLINK"}]
    positions, emissions, samples = {}, [], {}
    satellite_ids = [sat["satellite_id"] for sat in satellites]
    endpoints = {(devices[link["rx_id"]]["platform_type"], devices[link["rx_id"]]["platform_id"])
                 for link in downlinks}
    endpoints |= {("SATELLITE", sid) for sid in satellite_ids}
    for kind, pid in sorted(endpoints):
        klass = {"SATELLITE": "Satellite", "AIRCRAFT": "Aircraft", "GATEWAY": "Facility"}[kind]
        obj = root.GetObjectFromPath(f"*/{klass}/{pid}")
        provider = obj.DataProviders.Item("Cartesian Position")
        if kind == "GATEWAY":
            result = provider.Exec()
            xyz = tuple(float(_values(result, axis)[0]) for axis in ("x", "y", "z"))
            for instant in time_grid:
                positions[(kind, pid, instant)] = xyz
        else:
            result = provider.Group.Item("Fixed").ExecElements(0, (len(time_grid)-1)*step, step, ["x", "y", "z"])
            axes = [_values(result, axis) for axis in ("x", "y", "z")]
            if any(len(axis) != len(time_grid) for axis in axes):
                raise RuntimeError(f"{kind}/{pid}: Cartesian time-grid mismatch")
            for index, instant in enumerate(time_grid):
                positions[(kind, pid, instant)] = tuple(float(axis[index]) for axis in axes)

    for link in downlinks:
        tx, receiver = devices[link["tx_id"]], devices[link["rx_id"]]
        for sid in satellite_ids:
            emissions.append({"tx": tx, "antenna": antennas[tx["antenna_id"]], "satellite_id": sid,
                              "target": (receiver["platform_type"], receiver["platform_id"]),
                              "link_id": link["link_id"]})
    receivers = {link["rx_id"]: link for link in downlinks}
    # Cache one path per physical TX/satellite/victim receiver, not per serving satellite.
    cross_total = len(receivers) * len(emissions)
    progress.stage("INTERFERENCE", cross_total + len(budget_rows), "采样可见同频干扰路径")
    completed = 0
    for rid, victim_link in receivers.items():
        rx = devices[rid]
        rx_path = object_paths[(victim_link["link_id"], satellite_ids[0])][1]
        for emission in emissions:
            source, jsid = emission["tx"], emission["satellite_id"]
            completed += 1
            progress.update(completed, f"干扰路径 {jsid}/{source['device_id']} → {rid}")
            if abs(float(source["frequency_hz"]) - float(rx["frequency_hz"])) > 1:
                continue  # adjacent-channel interference is outside this model
            if spectral_overlap(source, rx) <= 0:
                continue
            visible_times = []
            for index, instant in enumerate(time_grid):
                if rx["platform_type"] == "AIRCRAFT":
                    visible = geometry_visible[(rx["platform_id"], jsid, instant)]
                else:
                    visible = feeder_geometry[(rx["platform_id"], jsid, instant)][0]
                if visible and (receiver_masks or {}).get((rid,jsid,instant), True):
                    visible_times.append((index, instant))
            if not visible_times:
                continue
            tx_path = object_paths[(emission["link_id"], jsid)][0]
            access = root.GetObjectFromPath(tx_path).GetAccessToObject(root.GetObjectFromPath(rx_path))
            access.ComputeAccess()
            intervals = [access.ComputedAccessIntervalTimes.GetInterval(i) for i in range(access.ComputedAccessIntervalTimes.Count)]
            provider = access.DataProviders.Item("Link Information")
            for index, instant in visible_times:
                second = index * step
                if not any(float(a)-1e-6 <= second <= float(b)+1e-6 for a,b in intervals):
                    raise RuntimeError(f"Visible interference path has no STK RF access: {tx_path} → {rx_path} at {instant}")
                point = provider.ExecSingle(second)
                rip = float(_values(point, "Rcvd. Iso. Power")[0])
                samples[(source["device_id"], jsid, rid, instant)] = {"visible": True, "rip_dbw": rip}
    lookup = {link["link_id"]: link for link in downlinks}
    details = []
    for index, budget in enumerate(budget_rows):
        link = lookup.get(budget["link_id"])
        if link is not None:
            rx = devices[link["rx_id"]]
            result, contributions = aggregate_downlink(budget, link, rx, antennas[rx["antenna_id"]], emissions, positions, samples)
            budget.update(result)
            details.extend(contributions)
        progress.update(cross_total+index+1, f"聚合 {budget['link_id']} · {budget['satellite_id']}")
    return details
