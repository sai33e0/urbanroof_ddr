class AreaNormalizer:

    AREA_MAP = {

        "hall of flat no.103": "Hall",
        "hall": "Hall",

        "bedroom": "Bedroom",
        "common bedroom": "Bedroom",

        "master bedroom": "Master Bedroom",
        "master bedroom of flat no.103": "Master Bedroom",

        "kitchen": "Kitchen",

        "common bathroom": "Common Bathroom",
        "common bathroom of flat no.103": "Common Bathroom",

        "master bedroom bathroom": "Master Bedroom Bathroom",

        "external wall": "External Wall",
        "external wall (interior side)": "External Wall",
        "external wall (affected by internal leakage)": "External Wall",

        "parking area": "Parking Area",

        "wc": "WC"
    }

    def normalize(self, area):

        if not area:
            return "Unknown"

        key = area.lower().strip()
        key = key.replace("  ", " ")
        key = key.replace("flat no. ", "flat no.")

        if "of flat no." in key:
            key = key.split("of flat no.")[0].strip()
            key = key.strip(",.- ")

        return self.AREA_MAP.get(key, area)