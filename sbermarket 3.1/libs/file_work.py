import csv
import json


def writeDataToCSV(filePath: str, headers: list, data: list) -> None:
    with open(filePath, "wt", encoding='utf-8', newline='') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerow(headers) if headers != None else ''
        writer.writerows(data)


def read_file(file) -> list:
    with open(file, 'r', encoding='utf-8') as f:
        json_array = json.load(f)

    return json_array
