"""Read-only STK inventory. Does not start STK or infer a license from installation."""

from __future__ import annotations

import json
import platform
import os
import struct
import sys
import winreg


def main() -> None:
    result = {"python": sys.version.split()[0], "python_bits": struct.calcsize("P") * 8,
              "platform": platform.platform(), "stk_registry_versions": [],
              "stk12_com_registered": False, "active_stk12": False,
              "stk_installed_file_version": None, "stk_active_version": None,
              "communications_license": "UNVERIFIED",
              "data_providers": "UNVERIFIED"}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AGI\STK") as key:
            index = 0
            while True:
                try:
                    result["stk_registry_versions"].append(winreg.EnumKey(key, index))
                    index += 1
                except OSError:
                    break
    except OSError:
        pass
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"STK12.Application\CLSID") as key:
            clsid, _ = winreg.QueryValueEx(key, None)
        result["stk12_com_registered"] = True
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"CLSID\{clsid}\LocalServer32") as key:
            command, _ = winreg.QueryValueEx(key, None)
        end = command.lower().find(".exe") + 4
        executable = command[:end].strip('"') if end >= 4 else ""
        if os.path.isfile(executable):
            import win32api

            info = win32api.GetFileVersionInfo(executable, "\\")
            ms, ls = info["FileVersionMS"], info["FileVersionLS"]
            result["stk_installed_file_version"] = ".".join(map(str, (ms >> 16, ms & 65535, ls >> 16, ls & 65535)))
        try:
            import win32com.client

            app = win32com.client.GetActiveObject("STK12.Application")
            result["active_stk12"] = True
            try:
                result["stk_active_version"] = str(app.Version)
            except Exception:
                pass
        except Exception:
            pass
    except Exception:
        pass
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
