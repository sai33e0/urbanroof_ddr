class DDRGenerator:

    def _first_page(self, area):
        for obs in area.get("inspection_observations", []) + area.get("thermal_observations", []):
            page = obs.get("page")
            if page not in [None, "", "Not Available"]:
                return page
        return "Not Available"

    def _flatten(self, items, field):
        values = []

        for item in items or []:
            value = item.get(field)
            if isinstance(value, list):
                values.extend(value)
            elif value not in [None, "", "Not Available"]:
                values.append(value)

        return values

    def generate(self, validated_data):

        areas = []

        for area in validated_data.get("areas", []):
            observations = []

            observations.append(
                {
                    "page": self._first_page(area),
                    "issue": area.get("issue", "Observation"),
                    "description": area.get("description", "Not Available"),
                    "severity": area.get("severity", "Not Available"),
                    "severity_reason": area.get("severity_reason", "Not Available"),
                    "root_cause": area.get("root_cause", "Not Available"),
                    "recommended_actions": area.get("recommended_actions", ["Not Available"]),
                    "additional_notes": area.get("additional_notes", ["Not Available"]),
                    "missing_information": area.get("missing_information", ["Not Available"]),
                    "inspection_images": area.get("inspection_images", []),
                    "thermal_images": area.get("thermal_images", []),
                    "conflict": area.get("conflict"),
                }
            )

            areas.append(
                {
                    "area_name": area.get("area_name", "Unknown Area"),
                    "observations": observations,
                }
            )

        return {
            "property": validated_data.get("property", {}),
            "property_issue_summary": validated_data.get("property_issue_summary", "Not Available"),
            "area_wise_observations": areas,
            "areas": areas,
            "probable_root_cause": validated_data.get("probable_root_cause", ["Not Available"]),
            "severity_assessment": validated_data.get("severity_assessment", ["Not Available"]),
            "recommended_actions": validated_data.get("recommended_actions", ["Not Available"]),
            "additional_notes": validated_data.get("additional_notes", ["Not Available"]),
            "missing_information": validated_data.get("missing_information", ["Not Available"]),
        }