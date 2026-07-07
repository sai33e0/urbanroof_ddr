from collections import defaultdict
import re

from src.normalizer import AreaNormalizer


def _dedupe_list(items):

    seen = set()
    cleaned = []

    for item in items:
        key = str(item)
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


def _canonical_area(area_name):
    if not area_name:
        return ""

    value = str(area_name).lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"of flat no\.?\s*\d+[a-z]?", "", value)
    value = re.sub(r"[\s,.-]+$", "", value)
    return value


class ObservationMerger:

    def __init__(self):
        self.area_normalizer = AreaNormalizer()

    def _page_image_map(self, parsed_pages):
        page_map = {}

        for page in parsed_pages or []:
            page_map[str(page.get("page"))] = page.get("images", [])

        return page_map

    def _normalize_observation(self, observation, page_image_map, source):

        page = observation.get("page", "Not Available")
        page_key = str(page)
        images = []

        if observation.get("image_reference"):
            images.append(observation["image_reference"])

        images.extend(page_image_map.get(page_key, [])[:2])

        observation_text = observation.get("issue") or observation.get("observation") or "Observation"

        return {
            "area": self.area_normalizer.normalize(
                observation.get("area")
            ),
            "issue": observation.get("issue") or observation.get("observation") or "Observation",
            "description": observation.get("description") or observation.get("observation") or "Not Available",
            "severity_hint": observation.get("severity_hint") or "Not Available",
            "page": page,
            "image_reference": _dedupe_list(images) or ["Image Not Available"],
            "source": source,
            "observation_text": observation_text,
        }

    def merge(self, inspection_json, thermal_json, inspection_pages=None, thermal_pages=None):

        inspection_page_map = self._page_image_map(inspection_pages)
        thermal_page_map = self._page_image_map(thermal_pages)

        merged = defaultdict(
            lambda: {
                "inspection": [],
                "thermal": [],
                "inspection_images": [],
                "thermal_images": [],
                "conflicts": [],
                "missing_information": []
            }
        )

        # --------------------
        # Inspection
        # --------------------
        for obs in inspection_json.get("observations", []):

            normalized = self._normalize_observation(
                obs,
                inspection_page_map,
                "inspection"
            )
            area = normalized["area"]

            if area == "Unknown":
                area = "Unmatched Inspection Findings"

            merged[area]["inspection"].append(normalized)
            merged[area]["inspection_images"].extend(normalized["image_reference"])

        # --------------------
        # Thermal
        # --------------------
        unmatched_thermal = []

        inspection_keys = list(merged.keys())

        for thermal in thermal_json.get("thermal_observations", []):
            normalized = self._normalize_observation(
                thermal,
                thermal_page_map,
                "thermal"
            )

            thermal_area = normalized["area"]

            match_area = None
            if thermal_area and thermal_area != "Not Available":
                thermal_key = _canonical_area(thermal_area)

                for inspection_area in inspection_keys:
                    inspection_key = _canonical_area(inspection_area)
                    if thermal_key == inspection_key or thermal_key in inspection_key or inspection_key in thermal_key:
                        match_area = inspection_area
                        break

            if match_area is None:
                unmatched_thermal.append(normalized)
                continue

            merged[match_area]["thermal"].append(normalized)
            merged[match_area]["thermal_images"].extend(normalized["image_reference"])

        if unmatched_thermal:
            merged["Unmatched Thermal Findings"]["thermal"].extend(unmatched_thermal)
            for thermal in unmatched_thermal:
                merged["Unmatched Thermal Findings"]["thermal_images"].extend(thermal["image_reference"])

        for area, data in merged.items():
            data["inspection_images"] = _dedupe_list(data["inspection_images"])
            data["thermal_images"] = _dedupe_list(data["thermal_images"])

        return dict(merged)