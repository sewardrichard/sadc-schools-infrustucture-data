# SADC Schools Infrastructure Data Extraction CLI

A Python CLI tool for extracting school location and profile data from the GigaMaps API for SADC (Southern African Development Community) countries.

## Overview

This script fetches comprehensive school data from the GigaMaps service and exports it to CSV files. It supports two main data types:

1. **School Locations**: Geographic coordinates, school names, education levels, and identifiers
2. **School Profiles**: Connectivity data, administrative regions, and infrastructure information

The tool automatically merges both datasets to create a master file with combined information.

## Supported Countries

The script extracts data for the following SADC countries (ISO3 codes):

- **ZAF** - South Africa
- **ZWE** - Zimbabwe
- **BWA** - Botswana
- **SWZ** - Eswatini
- **LSO** - Lesotho
- **MOZ** - Mozambique
- **NAM** - Namibia

## Features

- **Paginated API calls**: Handles large datasets with automatic pagination
- **Progress tracking**: Real-time progress bars using tqdm
- **Rate limiting**: Built-in delays to respect API rate limits
- **Flexible authentication**: API keys via CLI arguments or environment variables
- **Error handling**: Graceful handling of API errors with detailed logging
- **Data merging**: Automatic merging of location and profile data on school ID

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Dependencies

Install the required packages:

```bash
pip install pandas requests tqdm
```

Or create a `requirements.txt` file:

```
pandas>=1.3.0
requests>=2.26.0
tqdm>=4.62.0
```

Then install:

```bash
pip install -r requirements.txt
```

## Configuration

### API Keys

You need two API keys from GigaMaps:

1. **School Location API Key**: For fetching geographic school data
2. **School Profile API Key**: For fetching connectivity and infrastructure data

#### Option 1: .env File (Recommended)

Create a `.env` file in the project root directory with your API keys:

```env
GIGA_SCHOOL_LOCATION_API_KEY=your_location_api_key_here
GIGA_SCHOOL_PROFILE_API_KEY=your_profile_api_key_here
```

The script automatically loads environment variables from the `.env` file using `python-dotenv`.

#### Option 2: Environment Variables

Set the following environment variables:

```bash
export GIGA_SCHOOL_LOCATION_API_KEY="your_location_api_key"
export GIGA_SCHOOL_PROFILE_API_KEY="your_profile_api_key"
```

On Windows:

```cmd
set GIGA_SCHOOL_LOCATION_API_KEY=your_location_api_key
set GIGA_SCHOOL_PROFILE_API_KEY=your_profile_api_key
```

#### Option 3: Command Line Arguments

Pass API keys directly when running the script:

```bash
python giga_maps_cli.py --location-api-key "your_key" --profile-api-key "your_key"
```

#### Option 4: Interactive Prompt

The script will prompt for missing API keys during execution.

## Usage

### Basic Usage

Run the script with environment variables configured:

```bash
python giga_maps_cli.py
```

### With Command Line Arguments

```bash
python giga_maps_cli.py --location-api-key "your_location_key" --profile-api-key "your_profile_key"
```

### Execution Flow

1. **Step 1 - School Locations**: Fetches location data for all SADC countries
2. **Confirmation**: Prompts whether to proceed to Step 2
3. **Step 2 - School Profiles**: Fetches profile data for all SADC countries
4. **Merge**: Combines location and profile data into a master dataset

### Example Output

```
==================================================
GigaMaps SADC School Data Extraction CLI
==================================================

--- Step 1: Extracting School Locations ---
Fetching school locations for SADC countries: ZAF, ZWE, BWA, SWZ, LSO, MOZ, NAM

Processing ZAF...
  Fetching locations for ZAF: 100%|████████| 45/45 [00:15<00:00,  2.89page/s]
  Successfully fetched 43250 total locations for ZAF.

Processing ZWE...
  Fetching locations for ZWE: 100%|████████| 12/12 [00:04<00:00,  2.67page/s]
  Successfully fetched 11500 total locations for ZWE.

...

Total school locations extracted across all countries: 98750
School locations saved to 'sadc_school_locations.csv'

Do you want to proceed to Step 2 (Extract School Profiles and Merge)? (yes/no): yes

--- Step 2: Extracting School Profiles and Merging ---
Fetching school profiles for SADC countries: ZAF, ZWE, BWA, SWZ, LSO, MOZ, NAM

...

Total school profiles extracted across all countries: 95200
School profiles saved to 'sadc_school_profiles.csv'

Merging location and profile data...
Merged data saved to 'sadc_schools_master_data.csv'
Master file contains 98750 schools with combined location and profile data.

==================================================
Extraction process completed.
==================================================
```

## Output Files

The script generates three CSV files:

### 1. `sadc_school_locations.csv`

Contains school location data with the following schema:

| Column | Description |
|--------|-------------|
| `school_name` | Name of the school |
| `latitude` | Geographic latitude |
| `longitude` | Geographic longitude |
| `education_level` | Education level (primary, secondary, etc.) |
| `country_iso3_code` | ISO3 country code |
| `giga_id_school` | Unique Giga school identifier |
| `school_data_source` | Source of the school data |

### 2. `sadc_school_profiles.csv`

Contains school profile data with the following schema:

| Column | Description |
|--------|-------------|
| `giga_id_school` | Unique Giga school identifier |
| `school_area_type` | Type of school area (urban/rural) |
| `country_iso3_code` | ISO3 country code |
| `admin1` | First-level administrative division |
| `admin2` | Second-level administrative division |
| `connectivity` | Connectivity status |
| `connectivity_RT` | Real-time connectivity data |
| `connectivity_RT_datasource` | Source of RT connectivity data |
| `connectivity_type` | Type of connectivity |
| `school_data_source` | Source of the school data |

### 3. `sadc_schools_master_data.csv`

Merged dataset combining location and profile information. Join is performed on:
- `giga_id_school` (primary key)
- `country_iso3_code` (secondary key)

## API Endpoints

The script interacts with the following GigaMaps API endpoints:

- **Base URL**: `https://uni-ooi-giga-maps-service-dev.azurewebsites.net/api/v1`

### School Locations
- **Endpoint**: `/schools_location/country/{isocode3}`
- **Method**: GET
- **Parameters**: `page`, `size`
- **Authentication**: Bearer token

### School Profiles
- **Endpoint**: `/schools_profile`
- **Method**: GET
- **Parameters**: `country_iso3_code`, `page`, `size`
- **Authentication**: Bearer token

## Error Handling

The script includes comprehensive error handling:

- **Network timeouts**: 30-second timeout for API requests
- **HTTP errors**: Automatic retry on failed requests
- **Empty responses**: Graceful handling of missing data
- **Pagination errors**: Stops on incomplete pages
- **API key validation**: Prompts for missing keys

## Rate Limiting

To respect API rate limits:
- 0.2 second delay between paginated requests
- Page size: 1000 records per request

## Troubleshooting

### "Location API Key is required"
- Ensure `GIGA_SCHOOL_LOCATION_API_KEY` environment variable is set
- Or provide via `--location-api-key` argument

### "No locations found for {country}"
- Verify API key has access to the specified country
- Check network connectivity
- Ensure GigaMaps API is operational

### "Error on page X for {country}"
- Network timeout or API error
- Script continues with next country
- Check specific error message for details

### Merge produces fewer records than expected
- Some schools may not have profile data
- Check `sadc_school_profiles.csv` for coverage
- Left join ensures all location records are preserved

## License

This project is part of the SADC Schools Infrastructure Data initiative.

## Contact

For issues or questions about the GigaMaps API, refer to the official GigaMaps documentation.
