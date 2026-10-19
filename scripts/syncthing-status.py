#!/usr/bin/env python3
"""Print a readable, read-only status of the local Syncthing instance."""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


GUI_ADDRESS = "127.0.0.1:8384"


def config_path():
    result = subprocess.run(
        ["syncthing", "paths"], capture_output=True, text=True, check=True
    )
    match = re.search(r"^Configuration file:\s*\n\s*(.+)$", result.stdout, re.M)
    if not match:
        raise RuntimeError("syncthing paths에서 설정 파일 경로를 찾지 못했습니다")
    return match.group(1).strip()


def api_get(path, key):
    request = urllib.request.Request(
        f"http://{GUI_ADDRESS}{path}", headers={"X-API-Key": key}
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def format_completion(value):
    if value is None:
        return "확인 불가"
    return f"{value:g}%"


def table_cell(value):
    return str(value).replace("|", "¦").replace("\n", " ").replace("\t", " ")


def display_width(value):
    return sum(
        0 if unicodedata.combining(char) else
        2 if unicodedata.east_asian_width(char) in ("F", "W") else 1
        for char in value
    )


def print_table(headers, rows):
    widths = [max(display_width(row[i]) for row in [headers, *rows])
              for i in range(len(headers))]
    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    def print_row(row):
        cells = [cell + " " * (width - display_width(cell))
                 for cell, width in zip(row, widths)]
        print("| " + " | ".join(cells) + " |")

    print(border)
    print_row(headers)
    print(border)
    for row in rows:
        print_row(row)
    print(border)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", help="조회할 폴더 ID 또는 이름")
    args = parser.parse_args()

    root = ET.parse(config_path()).getroot()
    gui = root.find("gui")
    if gui is None or not gui.findtext("apikey"):
        raise RuntimeError("Syncthing 설정에서 로컬 API 키를 찾지 못했습니다")
    address = gui.findtext("address", "")
    if address != GUI_ADDRESS or gui.get("tls") == "true":
        raise RuntimeError(f"이 스크립트는 HTTP {GUI_ADDRESS} 설정에서만 실행합니다")
    key = gui.findtext("apikey")
    local_id = api_get("/rest/system/status", key)["myID"]
    connections = api_get("/rest/system/connections", key)["connections"]
    devices = {
        device.get("id"): device.get("name") or device.get("id", "")[:7]
        for device in root.findall("device")
    }
    folders = []
    has_problem = False
    has_disconnected_peer = False
    for folder in root.findall("folder"):
        folder_id = folder.get("id")
        label = folder.get("label") or folder_id
        if args.folder and args.folder not in (folder_id, label):
            continue
        params = urllib.parse.urlencode({"folder": folder_id})
        local = api_get("/rest/db/status?" + params, key)
        peers = []
        for shared in folder.findall("device"):
            device_id = shared.get("id")
            if not device_id:
                raise RuntimeError("공유 기기의 Device ID가 없습니다")
            if device_id == local_id:
                continue
            connection = connections.get(device_id, {})
            completion = api_get(
                "/rest/db/completion?"
                + urllib.parse.urlencode({"folder": folder_id, "device": device_id}),
                key,
            )
            connected = connection.get("connected", False)
            paused = connection.get("paused", False)
            if not connected:
                has_disconnected_peer = True
            if (not connected or paused or completion.get("completion") != 100
                    or completion.get("remoteState") != "valid"):
                has_problem = True
            peers.append(
                {
                    "name": devices.get(device_id, device_id[:7]),
                    "id_prefix": device_id[:7],
                    "connected": connected,
                    "paused": paused,
                    "completion": completion.get("completion"),
                    "remoteState": completion.get("remoteState"),
                }
            )
        if (local.get("state") != "idle" or local.get("needTotalItems")
                or local.get("pullErrors") or
                (folder.get("type") == "receiveonly" and
                 local.get("receiveOnlyTotalItems"))):
            has_problem = True
        folders.append(
            {
                "id": folder_id,
                "label": label,
                "type": folder.get("type"),
                "state": local.get("state"),
                "needTotalItems": local.get("needTotalItems"),
                "pullErrors": local.get("pullErrors"),
                "receiveOnlyTotalItems": local.get("receiveOnlyTotalItems"),
                "peers": peers,
            }
        )
    if args.folder and not folders:
        raise ValueError(f"폴더를 찾지 못했습니다: {args.folder}")

    errors = api_get("/rest/system/error", key).get("errors") or []
    has_problem |= bool(errors)
    print(f"Syncthing: {'문제 있음' if has_problem else '정상'} "
          f"(조회 기기: {devices.get(local_id, local_id[:7])})")
    for folder in folders:
        line = (f"\n{folder['label']} ({folder['type']}) — 로컬: {folder['state']}"
                f" · 대기 {folder['needTotalItems']} · 오류 {folder['pullErrors']}")
        if folder["type"] == "receiveonly":
            line += f" · 로컬 변경 {folder['receiveOnlyTotalItems']}"
        print(line)
        rows = []
        for peer in folder["peers"]:
            connection = ("일시정지" if peer["paused"] else
                          "연결됨" if peer["connected"] else "끊김")
            completion = format_completion(peer["completion"])
            name = table_cell(f"{peer['name']} ({peer['id_prefix']})")
            remote_state = table_cell(peer["remoteState"] or "확인 불가")
            rows.append((name, connection, completion, remote_state))
        print()
        print_table(("원격 기기", "연결", "완료율", "원격 상태"), rows)
    print("\n오류: 없음" if not errors else "\n오류:")
    for error in errors:
        print(f"  {error.get('when', '')} {error.get('message', '')}".strip())
    scope = "현재 기기의 인덱스 기준"
    if has_disconnected_peer:
        scope += "; 끊긴 기기의 완료율은 현재 파일 상태를 보장하지 않음"
    print(f"확인 범위: {scope}")


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        subprocess.CalledProcessError,
        ET.ParseError,
        KeyError,
        ValueError,
        urllib.error.URLError,
        RuntimeError,
    ) as error:
        print(f"Syncthing 상태 조회 실패: {error}", file=sys.stderr)
        sys.exit(1)
