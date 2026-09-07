"""Unit tests for cross-cutting model behavior: timestamp coercion, extra fields."""

from __future__ import annotations

from awsysco.models import Folder, Link


class TestTimestampCoercion:
    def test_iso_string_passes_through(self):
        link = Link.model_validate({"id": "x", "created": "2026-01-01T00:00:00Z"})
        assert link.created == "2026-01-01T00:00:00Z"

    def test_firestore_seconds_nanos_converted_to_iso(self):
        folder = Folder.model_validate(
            {"id": "f1", "createdAt": {"_seconds": 1735689600, "_nanoseconds": 0}}
        )
        assert folder.created_at == "2025-01-01T00:00:00Z"

    def test_firestore_alt_key_names_converted(self):
        folder = Folder.model_validate(
            {"id": "f1", "createdAt": {"seconds": 1735689600, "nanoseconds": 0}}
        )
        assert folder.created_at == "2025-01-01T00:00:00Z"

    def test_garbage_timestamp_keeps_raw_value_no_crash(self):
        folder = Folder.model_validate({"id": "f1", "createdAt": "not-a-timestamp"})
        assert folder.created_at == "not-a-timestamp"

    def test_dict_without_seconds_key_is_not_coerced(self):
        # Guards against over-eager coercion of a genuinely-unrelated dict value
        # (features/limits-style fields, which are typed to accept a dict).
        from awsysco.models import MeResponse

        me = MeResponse.model_validate({"uid": "u1", "features": {"foo": "bar"}})
        assert me.features == {"foo": "bar"}


class TestUnknownFieldsPreserved:
    def test_extra_fields_do_not_raise(self):
        link = Link.model_validate(
            {"id": "x", "shortCode": "abc", "someBrandNewField": {"nested": True}}
        )
        assert link.id == "x"
        assert link.model_extra["someBrandNewField"] == {"nested": True}
