import streamlit as st
from google.cloud import compute_v1
import os

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

def get_unattached_disks_all_zones(project_id):
    client = compute_v1.DisksClient()
    unattached_disks = []
    
    # aggregated_list returns a map of zones -> disks
    agg_list = client.aggregated_list(project=project_id)
    
    for zone, resp in agg_list:
        # zone is the name of the zone as a string, resp is a list of disks
        if 'disks' in resp:
            for disk in resp.disks:
                if not disk.users:
                    unattached_disks.append({
                        'Name': disk.name,
                        'Size (GB)': disk.size_gb,
                        'Zone': disk.zone.split('/')[-1],
                        'Creation Timestamp': disk.creation_timestamp
                    })
    
    return unattached_disks

def display_dashboard_all_zones(project_id):
    st.title("GCP Unattached Persistent Disks")
    st.subheader(f"Project: {project_id}")

    disks = get_unattached_disks_all_zones(project_id)

    if disks:
        st.write(f"Total Unattached Disks: {len(disks)}")
        st.table(disks)
    else:
        st.write("No unattached disks found.")

if __name__ == "__main__":
    project_id = st.text_input("Enter GCP Project ID:")

    if project_id:
        display_dashboard_all_zones(project_id)
