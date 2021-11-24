import pandas as pd
import numpy as np
import re


class WindPRO:
    """Load an exported WindPRO meteo text file into a pandas DataFrame."""

    def __init__(self, file):
        """
        Initiates the class.

        :param file: text file for a WindPRO meteo file
        """
        self.file = file

        # Constants
        self.SOF = "TimeStamp"  # start of file
        self.DTF = "%Y-%m-%d %H:%M"
        self.df = None

        # Set header to empty dictionary and extract header
        self.header = {}
        self._read_header()

        # Check extracted header
        if self._check_header():
            self._available_heights()  # Determine available heights in the file
            self._parser()  # Parse file

    def _read_header(self):
        """
        Locate and extract the desired parameters in the header of the text file.
        """
        # Desired parameters
        site_info = [
            ["lon", r"Longitude: 	(\d+.\d+)"],
            ["lat", r"Latitude: 	(\d+.\d+)"],
            ["dtf", r"Date time format:	(.*$)"],
            ["decsep", r"Decimal separator:	(.*$)"],
            ["grpsep", r"Digit group separator:	(.*$)"],
            ["disp", r"Displacement height \[m\]:	(\d+.\d+)"],
            ["utc_offset", r"UTC offset \[minutes\]:	((?:\-|\+)\d+)"],
        ]

        # Loop through lines in text file and extract until TimeStamp is reached
        with open(self.file, "r") as lines:
            for index, line in enumerate(lines):
                if not line.startswith(self.SOF):
                    for info in site_info:
                        if match := re.search(info[1], line):
                            self.header[info[0]] = match.group(1)
                else:
                    self.header["sof"] = index
                    self.header["parameters"] = line
                    break

    def _check_header(self):
        """
        Check that text file has been exported with fixed localization.
        """
        if "yyyy-MM-dd hh:mm" not in self.header["dtf"] or '"."' not in self.header["decsep"]:
            print("Time series not exported with fixed localization!")
            return False
        else:
            return True

    def _available_heights(self):
        """
        Determines the height from a string.
        """
        height_mask = r"_(\d+.\d)"
        self.heights = list(set(re.findall(height_mask, self.header["parameters"])))

    def _parser(self):
        """
        Parses available data for each desired parameter for all heights into individual pandas DataFrames.
        """
        # Desired parameters
        names = [
            ["spd", r"^MeanWindSpeedUID_(\d+.\d+)m\_?(\w+)?"],
            ["dir", r"^DirectionUID_(\d+.\d+)m\_?(\w+)?"],
            ["temp", r"^TemperatureUID_(\d+.\d+)m\_?(\w+)?"],
            ["turb", r"^TurbIntUID_(\d+.\d+)m\_?(\w+)?"],
            ["pressure", r"^PressureUID_(\d+.\d+)m\_?(\w+)?"],
            ["rh", r"^RelativeHumidityUID_(\d+.\d+)m\_?(\w+)?"],
            ["spd_status", r"^DataStatus_MeanWindSpeedUID_(\d+.\d+)m\_?(\w+)?"],
            ["dir_status", r"^DataStatus_DirectionUID_(\d+.\d+)m\_?(\w+)?"],
            ["temp_status", r"^DataStatus_TemperatureUID_(\d+.\d+)m\_?(\w+)?"],
            ["turb_status", r"^DataStatus_TurbIntUID_(\d+.\d+)m\_?(\w+)?"],
            ["pressure_status", r"^DataStatus_PressureUID_(\d+.\d+)m\_?(\w+)?"],
            ["rh_status", r"^DataStatus_RelativeHumidityUID_(\d+.\d+)m\_?(\w+)?"],
            ["sample_status", r"^SampleStatus_(\d+.\d+)m\_?(\w+)?"],
        ]

        # Assign heights as keys and populate with initial values
        usecols = {key: [0] for key in self.heights}
        usenames = {key: ["datetime"] for key in self.heights}

        # Extract relevant columns and their position
        for index, parameter in enumerate(self.header["parameters"].split("\t")):
            for name in names:
                if match := re.search(name[1], parameter):
                    usecols[match.group(1)].append(index)
                    usenames[match.group(1)].append(name[0])

        # Assign heights as keys
        self.df = {key: None for key in self.heights}

        # For each available height parse data into a pandas DataFrame
        for height in self.heights:
            self.df[height] = pd.read_table(
                self.file,
                delimiter="\t",
                skip_blank_lines=False,
                skiprows=self.header["sof"] + 2,
                usecols=usecols[height],
                names=usenames[height],
                low_memory=False,
            )

            # Clean data depending on status columns
            status_cols = [col for col in self.df[height].columns if "status" in col]
            other_cols = [col for col in self.df[height].columns if "status" not in col][1:]

            for status_col in status_cols:
                if "sample_status" in status_col:
                    self.df[height].loc[self.df[height][status_col] != 0, other_cols] = np.nan
                else:
                    self.df[height].loc[self.df[height][status_col] != 0, status_col.split("_")[0]] = np.nan

            # Create datetime
            self.df[height]["datetime"] = pd.to_datetime(self.df[height]["datetime"], format=self.DTF)

            # Set index
            self.df[height] = self.df[height].set_index("datetime")

            # Drop status columns
            self.df[height].drop(status_cols, axis=1, inplace=True)

            # Convert columns to float
            for column in self.df[height].columns:
                self.df[height][column] = pd.to_numeric(self.df[height][column], errors="coerce")
