from src.normalizer import AreaNormalizer
from src.deduplicator import ObservationDeduplicator
from src.cleaner import DataCleaner
from src.missing_detector import MissingInformationDetector


def _dedupe_preserve_order(items):
    seen = set()
    cleaned = []

    for item in items:
        key = str(item)
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    return cleaned


def _as_text(observations, key):
    parts = []

    for obs in observations:
        value = obs.get(key)
        if value and value != "Not Available":
            parts.append(str(value))

    return " ".join(parts).lower()


def _severity_rank(severity):
    severity = (severity or "").lower()
    if "high" in severity:
        return 3
    if "medium" in severity:
        return 2
    if "low" in severity:
        return 1
    return 0


def _normalize_severity(observation):
    hint = observation.get("severity_hint") or "Not Available"
    text = f"{observation.get('issue', '')} {observation.get('description', '')} {hint}".lower()

    if any(term in text for term in ["leak", "leakage", "moisture", "damp", "hotspot", "water ingress", "seepage"]):
        return "High"

    if any(term in text for term in ["crack", "hollow", "debond", "stain", "efflorescence"]):
        return "Medium"

    if hint and hint.lower() in ["low", "medium", "high", "critical"]:
        return hint.title()

    return "Not Available"


def _derive_root_cause(area_name, inspection, thermal, conflict):
    combined = " ".join(
        [
            _as_text(inspection, "issue"),
            _as_text(inspection, "description"),
            _as_text(thermal, "issue"),
            _as_text(thermal, "description"),
        ]
    )

    if conflict:
        return "Thermal moisture anomaly conflicts with inspection findings. Manual inspection recommended."

    if any(term in combined for term in ["water ingress", "leak", "seepage", "damp"]):
        return "Likely waterproofing failure or water ingress."

    if any(term in combined for term in ["moisture"]):
        return "Likely concealed moisture intrusion."

    if any(term in combined for term in ["hollow", "tile", "debond"]):
        return "Likely tile adhesion failure or hollow-sounding finish."

    if any(term in combined for term in ["crack"]):
        return "Likely substrate movement or localized structural stress."

    if any(term in combined for term in ["pipe", "plumbing"]):
        return "Possible concealed plumbing leakage."

    if inspection and not thermal:
        return "Inspection finding requires thermal confirmation."

    if thermal and not inspection:
        return "Thermal anomaly requires manual inspection."

    return "Not Available"


def _derive_recommendations(area_name, inspection, thermal, conflict):
    recommendations = []
    combined = " ".join(
        [
            _as_text(inspection, "issue"),
            _as_text(inspection, "description"),
            _as_text(thermal, "issue"),
            _as_text(thermal, "description"),
        ]
    )

    if conflict:
        recommendations.append("Manual inspection recommended.")

    if any(term in combined for term in ["water ingress", "leak", "seepage", "damp"]):
        recommendations.append("Inspect waterproofing and trace the source of water ingress.")

    if any(term in combined for term in ["moisture"]):
        recommendations.append("Confirm concealed moisture spread and check nearby finishes.")

    if any(term in combined for term in ["hollow", "tile", "debond"]):
        recommendations.append("Check tile adhesion and re-fix or replace loose areas.")

    if any(term in combined for term in ["crack"]):
        recommendations.append("Assess crack width and repair substrate or finish as required.")

    if any(term in combined for term in ["pipe", "plumbing"]):
        recommendations.append("Inspect concealed plumbing lines for leaks.")

    if not recommendations:
        recommendations.append("Carry out a site inspection and confirm the report findings.")

    return _dedupe_preserve_order(recommendations)


def _build_issue_summary(inspection, thermal):
    issues = []

    for obs in inspection + thermal:
        issue = obs.get("issue") or obs.get("description") or "Observation"
        if issue not in issues:
            issues.append(issue)

    return "; ".join(issues) if issues else "Not Available"
class DDRValidator:

    def __init__(self):
        self.area_normalizer = AreaNormalizer()
        self.deduplicator = ObservationDeduplicator()
        self.cleaner = DataCleaner()
        self.missing_detector = MissingInformationDetector()

    def validate(self, merged_data, property_info=None):

        if not merged_data:
            return {
                "property": property_info or {},
                "areas": [],
                "property_issue_summary": "Not Available",
                "probable_root_cause": ["Not Available"],
                "severity_assessment": ["Not Available"],
                "recommended_actions": ["Not Available"],
                "additional_notes": ["No observations available."],
                "missing_information": ["Inspection Observation Not Available.", "Thermal Observation Not Available."]
            }

        report = {
            "property": property_info or {},
            "areas": [],
            "property_issue_summary": "Not Available",
            "probable_root_cause": [],
            "severity_assessment": [],
            "recommended_actions": [],
            "additional_notes": [],
            "missing_information": []
        }

        all_root_causes = []
        all_severity = []
        all_recommendations = []
        all_notes = []
        all_missing = []
        affected_areas = []

        for area, data in merged_data.items():

            inspection = self.deduplicator.deduplicate(
                [self.cleaner.clean(obs) for obs in data.get("inspection", [])]
            )
            thermal = self.deduplicator.deduplicate(
                [self.cleaner.clean(obs) for obs in data.get("thermal", [])]
            )

            for obs in inspection + thermal:
                self.missing_detector.detect(obs)

            inspection_text = _as_text(inspection, "issue") + " " + _as_text(inspection, "description")
            thermal_text = _as_text(thermal, "issue") + " " + _as_text(thermal, "description")

            conflict = None
            if "no leakage" in inspection_text and "moisture" in thermal_text:
                conflict = (
                    "Inspection indicates no leakage. Thermal indicates possible moisture. Manual inspection recommended."
                )

            inspection_images = _dedupe_preserve_order(data.get("inspection_images", []))
            thermal_images = _dedupe_preserve_order(data.get("thermal_images", []))

            issue_summary = _build_issue_summary(inspection, thermal)
            root_cause = _derive_root_cause(area, inspection, thermal, conflict)
            recommendations = _derive_recommendations(area, inspection, thermal, conflict)

            severity_candidates = [_normalize_severity(obs) for obs in inspection + thermal]
            severity = "Not Available"
            if severity_candidates:
                severity = max(severity_candidates, key=_severity_rank)

            severity_reason = "Severity derived from the strongest available inspection or thermal evidence."
            if severity == "High":
                severity_reason = "High severity because the combined findings indicate active leakage, moisture, or a direct conflict needing urgent review."
            elif severity == "Medium":
                severity_reason = "Medium severity because the findings suggest localized deterioration or follow-up is needed."
            elif severity == "Low":
                severity_reason = "Low severity because the available observations suggest limited impact."
            elif severity == "Critical":
                severity_reason = "Critical severity because the combined evidence suggests major active water ingress or structural risk."

            missing_information = []
            if not inspection:
                missing_information.append("Inspection Observation Not Available.")
            if not thermal:
                missing_information.append("Thermal Observation Not Available.")
            if not inspection_images and not thermal_images:
                missing_information.append("Image Not Available.")
            if any(obs.get("page") in ["", None, "Not Available"] for obs in inspection + thermal):
                missing_information.append("Page Number Not Available.")
            if severity == "Not Available":
                missing_information.append("Severity Not Available.")
            if root_cause == "Not Available":
                missing_information.append("Root Cause Not Available.")
            if not recommendations:
                missing_information.append("Recommended Actions Not Available.")

            area_record = {
                "area_name": area,
                "issue": issue_summary,
                "description": self._compose_description(area, inspection, thermal, conflict),
                "inspection_observations": inspection,
                "thermal_observations": thermal,
                "inspection_images": inspection_images,
                "thermal_images": thermal_images,
                "severity": severity,
                "severity_reason": severity_reason,
                "root_cause": root_cause,
                "recommended_actions": recommendations,
                "additional_notes": _dedupe_preserve_order([
                    note for note in [conflict, f"Inspection images: {len(inspection_images)}", f"Thermal images: {len(thermal_images)}"] if note
                ]),
                "missing_information": _dedupe_preserve_order(missing_information),
                "conflict": conflict,
            }

            report["areas"].append(area_record)

            if area_record["issue"] != "Not Available":
                affected_areas.append(area)
            if root_cause != "Not Available":
                all_root_causes.append(root_cause)
            if severity != "Not Available":
                all_severity.append(f"{area}: {severity} ({severity_reason})")
            all_recommendations.extend(recommendations)
            all_notes.extend(area_record["additional_notes"])
            all_missing.extend(area_record["missing_information"])

        if affected_areas:
            report["property_issue_summary"] = (
                f"{len(affected_areas)} area(s) show diagnostics findings across the inspection and thermal reports: "
                + ", ".join(_dedupe_preserve_order(affected_areas))
            )

        if any(area.get("conflict") for area in report["areas"]):
            all_notes.append("Conflict detected between inspection and thermal evidence in one or more areas.")

        report["probable_root_cause"] = _dedupe_preserve_order(all_root_causes) or ["Not Available"]
        report["severity_assessment"] = _dedupe_preserve_order(all_severity) or ["Not Available"]
        report["recommended_actions"] = _dedupe_preserve_order(all_recommendations) or ["Not Available"]
        report["additional_notes"] = _dedupe_preserve_order(all_notes) or ["Not Available"]
        report["missing_information"] = _dedupe_preserve_order(all_missing) or ["Not Available"]

        return report

    def _compose_description(self, area, inspection, thermal, conflict):

        parts = []

        if inspection:
            inspection_bits = []
            for obs in inspection:
                observation = obs.get("issue") or obs.get("description") or "Observation"
                description = obs.get("description") or "Not Available"
                page = obs.get("page") or "Not Available"
                inspection_bits.append(f"Inspection page {page}: {observation} - {description}")
            parts.append("; ".join(inspection_bits))
        else:
            parts.append("Inspection Observation Not Available.")

        if thermal:
            thermal_bits = []
            for obs in thermal:
                observation = obs.get("issue") or obs.get("description") or obs.get("observation") or "Observation"
                description = obs.get("description") or obs.get("observation") or "Not Available"
                hotspot = obs.get("hotspot") or "Not Available"
                coldspot = obs.get("coldspot") or "Not Available"
                page = obs.get("page") or "Not Available"
                thermal_bits.append(
                    f"Thermal page {page}: {observation} - {description} (Hotspot {hotspot}, Coldspot {coldspot})"
                )
            parts.append("; ".join(thermal_bits))
        else:
            parts.append("Thermal Observation Not Available.")

        if conflict:
            parts.append(conflict)

        return " ".join(parts)