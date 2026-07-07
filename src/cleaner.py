class DataCleaner:

    def clean(self, observation):

        for key, value in observation.items():

            if value == "":

                observation[key] = "Not Available"

        return observation