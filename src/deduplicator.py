class ObservationDeduplicator:

    def deduplicate(self, observations):

        seen = set()

        cleaned = []

        for obs in observations:

            key = (

                obs.get("area"),

                obs.get("issue"),

                obs.get("description")

            )

            if key not in seen:

                seen.add(key)

                cleaned.append(obs)

        return cleaned