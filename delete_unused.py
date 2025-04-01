import streamlit as st
from google.cloud import compute_v1
import os
# Streamlit app to detect and delete unattached persistent disks in GCP

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"


# GCP Client Setup
def get_unattached_disks(project_id, zone):
    client = compute_v1.DisksClient()
    unattached_disks = []

    # List all disks in the specified zone
    for disk in client.list(project=project_id, zone=zone):
        if not disk.users:  # Check if disk is unattached
            unattached_disks.append({
                'Name': disk.name,
                'Size (GB)': disk.size_gb,
                'Zone': disk.zone.split('/')[-1],
                'Creation Timestamp': disk.creation_timestamp
            })

    return unattached_disks

# Cleanup unattached disks
def cleanup_unattached_disks(project_id, zone, disk_names):
    client = compute_v1.DisksClient()

    for disk_name in disk_names:
        disk = client.get(project=project_id, zone=zone, disk=disk_name)
        if disk:
            # Deleting the disk
            client.delete(project=project_id, zone=zone, disk=disk_name)
            st.success(f"Disk '{disk_name}' has been deleted.")

# Streamlit Dashboard
def display_dashboard(project_id, zone):
    st.title("GCP Unattached Persistent Disks")
    st.subheader(f"Project: {project_id} | Zone: {zone}")

    disks = get_unattached_disks(project_id, zone)

    if disks:
        st.write(f"Total Unattached Disks: {len(disks)}")
        st.table(disks)

        # Show cleanup option
        if st.checkbox('Enable Disk Cleanup'):
            disk_names = [disk['Name'] for disk in disks]
            st.write("The following disks will be deleted:")

            # Display disks to be deleted
            st.table([{'Name': disk_name} for disk_name in disk_names])

            # Confirmation prompt
            confirm_cleanup = st.button('Confirm Cleanup')

            if confirm_cleanup:
                cleanup_unattached_disks(project_id, zone, disk_names)
                st.write("Cleanup complete.")
    else:
        st.write("No unattached disks found.")

if __name__ == "__main__":
    project_id = st.text_input("Enter GCP Project ID:")
    zone = st.text_input("Enter Zone (e.g., us-central1-a):")

    if project_id and zone:
        display_dashboard(project_id, zone)
