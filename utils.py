import re

def parse_message(text):
    pattern = r"宛名:\s*(.+)\n金額:\s*(\d+)\n但書:\s*(.+)\n発行日:\s*(\d{4}-\d{2}-\d{2})\n税率:\s*(.+)"
    match = re.search(pattern, text)

    if not match:
        return None

    return {
        "name": match.group(1),
        "amount": match.group(2),
        "description": match.group(3),
        "date": match.group(4),
        "tax_rate": match.group(5)
    }

def upload_to_storage(file_path):
    # ここでアップロードの処理を実装（例: Google Drive, AWS S3など）
    return "https://example.com/" + file_path