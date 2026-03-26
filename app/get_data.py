import os
import csv

def get_aplist_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, "data")

    file_path = os.path.join(save_dir, "aplist.csv")

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "wait for crawling data... (CSV file not found)",
            "data": []
        }

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            data_list = [row for row in reader]

        return {
            "status": "success",
            "total_count": len(data_list),
            "data": data_list
        }

    except Exception as e:
        print(f"CSV 파일을 읽는 중 오류 발생: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }