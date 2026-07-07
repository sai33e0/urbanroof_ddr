class MissingInformationDetector:

    def detect(self, observation):

        missing = []

        if observation.get("page") in ["", None, "Not Available"]:
            missing.append("Page Number")

        if observation.get("severity_hint") in ["", None, "Not Available"]:
            missing.append("Severity")

        if observation.get("image_reference") in ["", None, "Not Available"]:
            missing.append("Image")

        if observation.get("description") in ["", None, "Not Available"]:
            missing.append("Description")

        observation["missing_information"] = missing

        return observation