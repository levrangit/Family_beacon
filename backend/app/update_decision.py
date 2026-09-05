from datetime import datetime, timezone

from fastapi import HTTPException

from app.supabase_client import get_user_client


COMPONENT = "agent"
DEVICE_NOT_FOUND = "Device not found"


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid semantic version: {version}")
    return tuple(int(part) for part in parts)


def _is_compatible(
    current_version: tuple[int, int, int],
    compatibility: dict,
) -> bool:
    minimum = compatibility.get("min_agent_version")
    maximum = compatibility.get("max_agent_version")

    if minimum is not None and current_version < _version_tuple(minimum):
        return False

    if maximum is not None and current_version > _version_tuple(maximum):
        return False

    return True


def check_device_update(access_token: str, device_id: str):
    try:
        client = get_user_client(access_token)

        device_response = (
            client
            .table("devices")
            .select(
                "id, platform, agent_version, target_agent_version, update_status"
            )
            .eq("id", device_id)
            .maybe_single()
            .execute()
        )

        if device_response.data is None:
            raise HTTPException(status_code=404, detail=DEVICE_NOT_FOUND)

        device = device_response.data
        current_version = device.get("agent_version")

        if not current_version:
            return {
                "update_available": False,
                "component": COMPONENT,
                "device_id": device_id,
                "current_version": None,
                "target_version": None,
                "release_id": None,
                "reason": "agent_version_unknown",
            }

        try:
            current_version_tuple = _version_tuple(current_version)
        except ValueError as exc:
            raise HTTPException(
                status_code=500,
                detail="Device agent version is invalid",
            ) from exc

        now = datetime.now(timezone.utc).isoformat()
        releases_response = (
            client
            .table("component_releases")
            .select(
                "id, component, version, artifact_ref, checksum, "
                "release_notes, published_at"
            )
            .eq("component", COMPONENT)
            .lte("published_at", now)
            .execute()
        )
        releases = releases_response.data or []

        if not releases:
            return {
                "update_available": False,
                "component": COMPONENT,
                "device_id": device_id,
                "current_version": current_version,
                "target_version": None,
                "release_id": None,
                "reason": "no_release",
            }

        release_ids = [release["id"] for release in releases]
        compatibility_response = (
            client
            .table("component_compatibility")
            .select(
                "id, release_id, platform, min_agent_version, max_agent_version"
            )
            .eq("platform", device["platform"])
            .in_("release_id", release_ids)
            .execute()
        )
        compatibility_by_release = {
            row["release_id"]: row
            for row in (compatibility_response.data or [])
        }

        candidates = []
        for release in releases:
            try:
                release_version = _version_tuple(release["version"])
            except ValueError as exc:
                raise HTTPException(
                    status_code=500,
                    detail="Component release contains an invalid version",
                ) from exc

            if release_version <= current_version_tuple:
                continue

            compatibility = compatibility_by_release.get(release["id"])
            if compatibility is None:
                continue

            if not _is_compatible(current_version_tuple, compatibility):
                continue

            candidates.append((release_version, release))

        if not candidates:
            return {
                "update_available": False,
                "component": COMPONENT,
                "device_id": device_id,
                "current_version": current_version,
                "target_version": None,
                "release_id": None,
                "reason": "no_compatible_update",
            }

        _, target = max(candidates, key=lambda item: item[0])

        return {
            "update_available": True,
            "component": COMPONENT,
            "device_id": device_id,
            "current_version": current_version,
            "target_version": target["version"],
            "release_id": target["id"],
            "artifact_ref": target["artifact_ref"],
            "checksum": target["checksum"],
            "release_notes": target["release_notes"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to check device update",
        ) from exc
