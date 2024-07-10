from agency_swarm.tools import BaseTool
import os

from pydantic import Field

HEADER = 'id,name,brewery_type,address_1,address_2,city,state_province,postal_code,country,phone,' \
         'website_url,longitude,latitude'


class BreweryType:
    MICRO = "micro"  # Most craft breweries. For example, Samuel Adams is still considered a micro brewery.
    NANO = "nano"  # An extremely small brewery which typically only distributes locally.
    REGIONAL = "regional"  # A regional location of an expanded brewery.
    BREWPUB = "brewpub"  # A beer-focused restaurant or restaurant/bar with a brewery on-premise.
    LARGE = "large"  # A very large brewery. Likely not for visitors.
    PLANNING = "planning"  # A brewery in planning or not yet opened to the public.
    CONTRACT = "contract"  # A brewery that uses another brewery’s equipment.
    PROPRIETOR = "proprietor"  # Similar to contract brewing but refers more to a brewery incubator.
    CLOSED = "closed"  # A location which has been closed.


class FileProcessorTool(BaseTool):
    """
    FileProcessorTool is designed to update or create CSV files with brewery information in the format:
    id,name,brewery_type,address_1,address_2,address_3,city,state_province,postal_code,country,phone,website_url,longitude,latitude
    Mandatory fields are name, city, state_province, country, and brewery_type.
    In order to create or update a file, the tool requires the checkout directory where the git repository is located.
    Individual file names are expected in the format: checkout_directory/country/state_province.csv
    """

    checkout_directory: str = Field(
        None, description="The checkout directory where the repository is located. Mandatory."
    )
    KEY_COLUMN: int = 1  # Name is the key
    name: str = Field(
        None, description="The name of the brewery. Mandatory."
    )
    brewery_type: str = Field(
        "", description="The brewery type. Mandatory."
    )
    address_1: str = Field(
        "", description="The first line of the address."
    )
    address_2: str = Field(
        "", description="The second line of the address."
    )
    city: str = Field(
        None, description="The city for the brewery. Mandatory."
    )
    state_province: str = Field(
        None, description="The state or province for the brewery. Mandatory."
    )
    postal_code: str = Field(
        "", description="The postal code for the brewery."
    )
    country: str = Field(
        None, description="The country for the brewery. Mandatory."
    )
    phone: str = Field(
        "", description="The phone number for the brewery."
    )
    website_url: str = Field(
        "", description="The website URL for the brewery."
    )
    longitude: str = Field(
        "", description="The longitude for the brewery."
    )
    latitude: str = Field(
        "", description="The latitude for the brewery."
    )

    @staticmethod
    def validate_mandatory_field(field_name, value):
        if value is None:
            raise ValueError(f"{field_name} is mandatory.")

    @staticmethod
    def validate_brewery_type(type_str: str):
        if (type_str in [
            BreweryType.MICRO, BreweryType.NANO, BreweryType.REGIONAL, BreweryType.BREWPUB,
            BreweryType.LARGE, BreweryType.PLANNING, BreweryType.CONTRACT, BreweryType.PROPRIETOR,
            BreweryType.CLOSED
        ]) is False:
            raise ValueError(f"Invalid brewery type: {type_str}")

    def run(self, **kwargs):
        # Validation makes the tool more robust and easy to correct
        self.validate_mandatory_field("name", self.name)
        self.validate_mandatory_field("brewery_type", self.brewery_type)
        self.validate_brewery_type(self.brewery_type)
        self.validate_mandatory_field("city", self.city)
        self.validate_mandatory_field("state_province", self.state_province)
        self.validate_mandatory_field("country", self.country)
        self.validate_mandatory_field("checkout_directory", self.checkout_directory)
        self.validate_file_exists(self.checkout_directory)
        # The checking and adding
        file_path = os.path.join(self.checkout_directory, self.country, self.state_province + ".csv")
        if (self.check_file_exists(file_path)) is True:
            data_dict = self.read_file(file_path)
            if self.name not in data_dict:
                self.append_to_file(file_path)
        else:
            self.write_to_new_file(file_path)

    @staticmethod
    def check_file_exists(file_path: str):
        return os.path.exists(file_path)

    def validate_file_exists(self, file_path: str):
        if not self.check_file_exists(file_path):
            raise ValueError(f"File {file_path} does not exist.")

    def create_data_line(self):
        return f",{self.name},{self.brewery_type},{self.address_1},{self.address_2},{self.city},{self.state_province}" \
               f",{self.postal_code},{self.country},{self.phone},{self.website_url},{self.longitude},{self.latitude}"

    def read_file(self, file_path: str):
        with open(file_path, 'r') as file:
            data_dict = {}
            for line in file:
                values = line.split(',')
                if values[0] == 'id':  # Skip header
                    continue
                if len(values) > self.KEY_COLUMN:
                    key = values[self.KEY_COLUMN]
                    data_dict[key] = line.replace('\n', '')
            return data_dict

    def write_to_new_file(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(HEADER)
            file.write('\n')
            file.write(self.create_data_line())

    def append_to_file(self, file_path: str):
        last_line = ''
        with open(file_path, 'r') as file:
            for line in file:
                last_line = line
        with open(file_path, 'a') as file:
            if not last_line.endswith('\n'):
                file.write('\n')
            file.write(self.create_data_line())


# Example usage
if __name__ == "__main__":
    file_processor = FileProcessorTool(name="ABC", brewery_type="micro", city="New York", state_province="NY",
                                       country="USA", checkout_directory=".")
    file_processor.run()
