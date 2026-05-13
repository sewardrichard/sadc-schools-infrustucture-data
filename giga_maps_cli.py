import argparse
import os
import sys
import pandas as pd
import requests
from typing import List, Dict, Optional
import time
from tqdm import tqdm
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()

# --- Constants and Configuration ---
SADC_COUNTRIES_ISO3 = ["ZAF", "ZWE", "BWA", "SWZ", "LSO", "MOZ", "NAM"]
BASE_URL = os.getenv(
    "GIGA_MAPS_BASE_URL",
    "https://uni-ooi-giga-maps-service.azurewebsites.net/api/v1",
)
MAX_PAGE_SIZE = 100  # API enforces a maximum of 100 items per page

# --- API Client Functions ---

def validate_api_key(api_key: str, endpoint_label: str) -> bool:
    """
    Validates the API key by making a lightweight test request.
    Returns True if the key is valid, False otherwise.
    """
    url = f"{BASE_URL}/schools_location/country/ZAF"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    params = {"page": 1, "size": 1}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 401:
            error_body = ""
            try:
                error_body = response.json().get("message", response.text)
            except Exception:
                error_body = response.text
            print(f"\n  Authentication failed for {endpoint_label}: {error_body}")
            print("  Please verify that:")
            print("    1. Your API key (Bearer token) is correct and has not expired.")
            print("    2. The key was copied in full without extra spaces or missing characters.")
            print("    3. The key is a valid JWT issued by the GigaMaps API portal.")
            return False
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n  Could not connect to the GigaMaps API at {BASE_URL}.")
        print("  Please check your internet connection and try again.")
        return False
    except Exception as e:
        print(f"\n  Unexpected error during API key validation: {e}")
        return False


def fetch_school_locations(country_code: str, api_key: str) -> List[Dict]:
    """
    Fetches school location data for a given country.
    Endpoint: /schools_location/country/{isocode3}
    """
    url = f"{BASE_URL}/schools_location/country/{country_code}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    all_data = []
    page = 1
    size = MAX_PAGE_SIZE
    
    with tqdm(desc=f"  Fetching locations for {country_code}", unit="page") as pbar:
        while True:
            params = {"page": page, "size": size}
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                if response.status_code == 401:
                    print(f"\n  Authentication failed for {country_code}. Check your API key.")
                    break
                response.raise_for_status()
                
                data = response.json()
                records = data.get('data', [])
                if not records:
                    break
                    
                all_data.extend(records)
                pbar.update(1)
                pbar.set_postfix({"total": len(all_data)})
                
                if len(records) < size:
                    break
                page += 1
                time.sleep(0.2)
            except requests.exceptions.HTTPError as e:
                print(f"\n  HTTP error on page {page} for {country_code}: {e}")
                break
            except Exception as e:
                print(f"\n  Error on page {page} for {country_code}: {e}")
                break
        
    return all_data

def fetch_school_profiles(country_code: str, api_key: str) -> List[Dict]:
    """
    Fetches school profile data for a given country.
    Endpoint: /schools_profile/
    """
    url = f"{BASE_URL}/schools_profile/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    all_data = []
    page = 1
    size = MAX_PAGE_SIZE
    
    with tqdm(desc=f"  Fetching profiles for {country_code}", unit="page") as pbar:
        while True:
            params = {
                "country_iso3_code": country_code,
                "page": page,
                "size": size
            }
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                if response.status_code == 401:
                    print(f"\n  Authentication failed for {country_code}. Check your API key.")
                    break
                response.raise_for_status()
                
                data = response.json()
                records = data.get('data', [])
                if not records:
                    break
                    
                all_data.extend(records)
                pbar.update(1)
                pbar.set_postfix({"total": len(all_data)})
                
                if len(records) < size:
                    break
                page += 1
                time.sleep(0.2)
            except requests.exceptions.HTTPError as e:
                print(f"\n  HTTP error on page {page} for {country_code}: {e}")
                break
            except Exception as e:
                print(f"\n  Error on page {page} for {country_code}: {e}")
                break
        
    return all_data

# --- Main CLI Logic ---

def main():
    parser = argparse.ArgumentParser(description="Extract SADC school data from GigaMaps API.")
    parser.add_argument("--location-api-key", type=str, help="API key for school location data.")
    parser.add_argument("--profile-api-key", type=str, help="API key for school profile data.")
    args = parser.parse_args()

    location_api_key = args.location_api_key or os.getenv("GIGA_SCHOOL_LOCATION_API_KEY")
    profile_api_key = args.profile_api_key or os.getenv("GIGA_SCHOOL_PROFILE_API_KEY")

    all_locations_df = pd.DataFrame()
    all_profiles_df = pd.DataFrame()

    print("\n" + "="*50)
    print("GigaMaps SADC School Data Extraction CLI")
    print("="*50)

    # --- Step 1: Extracting School Locations ---
    print("\n--- Step 1: Extracting School Locations ---")
    if not location_api_key:
        location_api_key = input("Please enter your Giga School Location API Key: ").strip()
        if not location_api_key:
            print("Location API Key is required. Exiting.")
            return

    print("Validating Location API key...")
    if not validate_api_key(location_api_key, "School Location API"):
        print("\nFailed to authenticate with the GigaMaps Location API. Exiting.")
        return
    print("  API key is valid!")

    print(f"\nFetching school locations for SADC countries: {', '.join(SADC_COUNTRIES_ISO3)}")
    for country_code in SADC_COUNTRIES_ISO3:
        print(f"\nProcessing {country_code}...")
        try:
            locations = fetch_school_locations(country_code, location_api_key)
            if locations:
                df_loc = pd.DataFrame(locations)
                # Ensure the columns match the schema provided by the user
                # Schema: school_name, latitude, longitude, education_level, country_iso3_code, giga_id_school, school_data_source
                all_locations_df = pd.concat([all_locations_df, df_loc], ignore_index=True)
                print(f"  Successfully fetched {len(df_loc)} total locations for {country_code}.")
            else:
                print(f"  No locations found for {country_code}.")
        except Exception as e:
            print(f"  Error processing {country_code}: {e}")

    if not all_locations_df.empty:
        print(f"\nTotal school locations extracted across all countries: {len(all_locations_df)}")
        all_locations_df.to_csv("sadc_school_locations.csv", index=False)
        print("School locations saved to 'sadc_school_locations.csv'")
    else:
        print("No school locations extracted. Exiting.")
        return

    # --- Step 2: Extracting School Profiles and Merging ---
    proceed_to_step2 = input("\nDo you want to proceed to Step 2 (Extract School Profiles and Merge)? (yes/no): ").strip().lower()
    if proceed_to_step2 == "yes":
        print("\n--- Step 2: Extracting School Profiles and Merging ---")
        if not profile_api_key:
            profile_api_key = input("Please enter your Giga School Profile API Key: ").strip()
            if not profile_api_key:
                print("Profile API Key is required for Step 2. Exiting.")
                return

        print("Validating Profile API key...")
        if not validate_api_key(profile_api_key, "School Profile API"):
            print("\nFailed to authenticate with the GigaMaps Profile API. Exiting.")
            return
        print("  API key is valid!")

        print(f"\nFetching school profiles for SADC countries: {', '.join(SADC_COUNTRIES_ISO3)}")
        for country_code in SADC_COUNTRIES_ISO3:
            print(f"\nProcessing {country_code}...")
            try:
                profiles = fetch_school_profiles(country_code, profile_api_key)
                if profiles:
                    df_prof = pd.DataFrame(profiles)
                    # Schema: giga_id_school, school_area_type, country_iso3_code, admin1, admin2, connectivity, connectivity_RT, connectivity_RT_datasource, connectivity_type, school_data_source
                    all_profiles_df = pd.concat([all_profiles_df, df_prof], ignore_index=True)
                    print(f"  Successfully fetched {len(df_prof)} total profiles for {country_code}.")
                else:
                    print(f"  No profiles found for {country_code}.")
            except Exception as e:
                print(f"  Error processing {country_code}: {e}")

        if not all_profiles_df.empty:
            print(f"\nTotal school profiles extracted across all countries: {len(all_profiles_df)}")
            all_profiles_df.to_csv("sadc_school_profiles.csv", index=False)
            print("School profiles saved to 'sadc_school_profiles.csv'")

            print("\nMerging location and profile data...")
            # Using giga_id_school as the primary key for joining
            # We also include country_iso3_code in the join to be safe
            master_df = pd.merge(
                all_locations_df,
                all_profiles_df,
                on=['giga_id_school', 'country_iso3_code'],
                how='left',
                suffixes=('_loc', '_prof')
            )
            
            # Clean up redundant columns if any
            if 'school_data_source_loc' in master_df.columns and 'school_data_source_prof' in master_df.columns:
                master_df['school_data_source'] = master_df['school_data_source_loc'].fillna(master_df['school_data_source_prof'])
                master_df.drop(columns=['school_data_source_loc', 'school_data_source_prof'], inplace=True)

            master_df.to_csv("sadc_schools_master_data.csv", index=False)
            print("Merged data saved to 'sadc_schools_master_data.csv'")
            print(f"Master file contains {len(master_df)} schools with combined location and profile data.")
        else:
            print("No school profiles extracted. Skipping merge.")
    else:
        print("Skipping Step 2: School Profile Extraction and Merge.")

    print("\n" + "="*50)
    print("Extraction process completed.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
