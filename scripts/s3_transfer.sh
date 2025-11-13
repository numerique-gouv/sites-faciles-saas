#!/bin/bash

# Retrieve data from the old Clever Cloud bucket and migrate it to new dedicated buckets
# on an object storage belonging to the OPI

# Can be launched again to sync the contents, as long as there are no duplicate locations

# Profile names:
# clever → old storage, hosted by Clever Cloud
# ovh → old storage, hosted by OVH
# opi → new storage
# cf. https://help.ovhcloud.com/csm/fr-public-cloud-storage-s3-rclone?id=kb_article_view&sysparm_article=KB0047465 for config


echo "Please choose a source to sync:"
echo "1) Clever Cloud"
echo "2) OVH"
read -p "Enter your choice [1 or 2]: " CHOICE

case "${CHOICE}" in
    1)
        STORAGE="clever:storage-demo"
        ;;
    2)
        STORAGE="ovh:suite-numerique-staging"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

for DIR in $(rclone lsf ${STORAGE} --dirs-only | sed 's:/$::'); do
    echo "Processing $DIR"
    rclone mkdir opi:$DIR
    rclone sync ${STORAGE}/$DIR opi:$DIR/$DIR/ --progress
done
