import os
import platform
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET


class WindowsAppBlocker:
    def block(self, app: str) -> dict:
        if not app:
            raise ValueError("app is required")

        app = app.strip()

        if not app:
            raise ValueError("app is required")

        if platform.system() != "Windows":
            raise RuntimeError(
                "Block app command is supported only on Windows"
            )

        self._apply_block_rule(app)

        return {
            "status": "app_blocked",
            "app": app,
        }

    def unblock(self, app: str) -> dict:
        if not app:
            raise ValueError("app is required")

        app = app.strip()

        if not app:
            raise ValueError("app is required")

        if platform.system() != "Windows":
            raise RuntimeError(
                "Unblock app command is supported only on Windows"
            )

        self._remove_block_rule(app)

        return {
            "status": "app_unblocked",
            "app": app,
        }

    @staticmethod
    def _remove_block_rule(app: str) -> None:
        powershell_script = r"""
$ErrorActionPreference = "Stop"

$policy = Get-AppLockerPolicy -Local -Xml

[xml]$xml = $policy

$namespace = @{
    app = "http://schemas.microsoft.com/CodeSigning/2006/08/Policy"
}

$rules = $xml.AppLockerPolicy.RuleCollection.FilePathRule

foreach ($rule in @($rules)) {
    if (
        $rule.Name -eq "Family Beacon Block $env:FAMILY_BEACON_APP"
    ) {
        $rule.ParentNode.RemoveChild($rule) | Out-Null
    }
}

$tempPolicy = [System.IO.Path]::GetTempFileName()

try {
    $xml.Save($tempPolicy)

    Set-AppLockerPolicy `
        -XmlPolicy $tempPolicy `
        -Merge
}
finally {
    if (Test-Path $tempPolicy) {
        Remove-Item $tempPolicy -Force
    }
}
"""

        env = os.environ.copy()
        env["FAMILY_BEACON_APP"] = app

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script,
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    @staticmethod
    def _build_policy_xml(app: str) -> str:
        namespace = (
            "http://schemas.microsoft.com/CodeSigning/2006/08/Policy"
        )

        ET.register_namespace("", namespace)

        policy = ET.Element(
            f"{{{namespace}}}AppLockerPolicy",
            {
                "Version": "1",
            },
        )

        rule_collection = ET.SubElement(
            policy,
            f"{{{namespace}}}RuleCollection",
            {
                "Type": "Exe",
                "EnforcementMode": "Enabled",
            },
        )

        rule = ET.SubElement(
            rule_collection,
            f"{{{namespace}}}FilePathRule",
            {
                "Id": "{" + str(uuid.uuid4()) + "}",
                "Name": f"Family Beacon Block {app}",
                "Description": (
                    f"Blocked by Family Beacon: {app}"
                ),
                "UserOrGroupSid": "S-1-1-0",
                "Action": "Deny",
            },
        )

        conditions = ET.SubElement(
            rule,
            f"{{{namespace}}}Conditions",
        )

        path_condition = ET.SubElement(
            conditions,
            f"{{{namespace}}}FilePathCondition",
        )

        ET.SubElement(
            path_condition,
            f"{{{namespace}}}Path",
        ).text = f"*\\{app}"

        return ET.tostring(
            policy,
            encoding="unicode",
        )

    @staticmethod
    def _apply_block_rule(app: str) -> None:
        policy_xml = WindowsAppBlocker._build_policy_xml(app)

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".xml",
                prefix="family_beacon_applocker_",
                delete=False,
                encoding="utf-8",
            ) as policy_file:
                policy_file.write(policy_xml)
                temp_path = policy_file.name

            powershell_script = r"""
$ErrorActionPreference = "Stop"

Set-AppLockerPolicy `
    -XmlPolicy $env:FAMILY_BEACON_APPLOCKER_POLICY `
    -Merge
"""

            env = os.environ.copy()
            env["FAMILY_BEACON_APPLOCKER_POLICY"] = temp_path

            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    powershell_script,
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
