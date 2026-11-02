"""List files in a Kaggle dataset. This does not download the archive.

kagglehub 1.0.3 has dataset_download and no dataset_list_files. The call below
uses the dataset file-list API only.
"""

from kagglehub.clients import build_kaggle_client
from kagglesdk.datasets.types.dataset_api_service import ApiListDatasetFilesRequest

DATASET = "pypiahmad/librispeech-asr-corpus"


def main() -> None:
    owner, slug = DATASET.split("/", 1)
    client = build_kaggle_client()
    page_token = ""
    count = 0
    while True:
        request = ApiListDatasetFilesRequest()
        request.owner_slug = owner
        request.dataset_slug = slug
        request.page_size = 200
        if page_token:
            request.page_token = page_token
        response = client.datasets.dataset_api_client.list_dataset_files(request)
        if response.error_message:
            raise SystemExit(response.error_message)
        batch = response.dataset_files or []
        for item in batch:
            count += 1
            print(f"{item.total_bytes}\t{item.name}")
        page_token = response.next_page_token
        if not page_token:
            break
    if count == 0:
        raise SystemExit("The file list was empty. No archive was downloaded.")


if __name__ == "__main__":
    main()
