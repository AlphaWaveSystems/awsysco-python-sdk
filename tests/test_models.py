"""Unit tests for cross-cutting model behavior: timestamp coercion, extra fields."""

from __future__ import annotations

from awsysco.models import Folder, Link, LinkList


class TestTimestampCoercion:
    def test_iso_string_passes_through(self):
        link = Link.model_validate({"id": "x", "created": "2026-01-01T00:00:00Z"})
        assert link.created == "2026-01-01T00:00:00Z"

    def test_firestore_seconds_nanos_converted_to_iso(self):
        folder = Folder.model_validate(
            {"id": "f1", "createdAt": {"_seconds": 1735689600, "_nanoseconds": 0}}
        )
        assert folder.created_at == "2025-01-01T00:00:00Z"

    def test_firestore_timestamp_converted_on_a_real_link_response(self):
        """The coercion is a base-model validator (applies to every model), but
        it must be checked against Link specifically — the primary response type —
        not only against a secondary model like Folder."""
        link = Link.model_validate(
            {
                "id": "abc123",
                "shortCode": "abc123",
                "created": {"_seconds": 1735689600, "_nanoseconds": 0},
                "expiresAt": {"seconds": 1735776000, "nanoseconds": 500000000},
            }
        )
        assert link.created == "2025-01-01T00:00:00Z"
        assert link.expires_at == "2025-01-02T00:00:00.500000Z"

    def test_firestore_alt_key_names_converted(self):
        folder = Folder.model_validate(
            {"id": "f1", "createdAt": {"seconds": 1735689600, "nanoseconds": 0}}
        )
        assert folder.created_at == "2025-01-01T00:00:00Z"

    def test_garbage_timestamp_keeps_raw_value_no_crash(self):
        folder = Folder.model_validate({"id": "f1", "createdAt": "not-a-timestamp"})
        assert folder.created_at == "not-a-timestamp"

    def test_non_numeric_nanoseconds_never_raises(self):
        """A TypeError from `nanos / 1e9` when nanos isn't numeric must not escape —
        it must be caught same as the numeric-but-out-of-range cases below."""
        folder = Folder.model_validate(
            {"id": "f1", "createdAt": {"seconds": 1, "nanoseconds": "q"}}
        )
        assert isinstance(folder.created_at, str)

    def test_huge_seconds_never_raises(self):
        folder = Folder.model_validate({"id": "f1", "createdAt": {"_seconds": 1e300}})
        assert isinstance(folder.created_at, str)

    def test_very_negative_seconds_never_raises(self):
        folder = Folder.model_validate({"id": "f1", "createdAt": {"seconds": -1e14}})
        assert isinstance(folder.created_at, str)

    def test_list_valued_seconds_never_raises(self):
        folder = Folder.model_validate({"id": "f1", "createdAt": {"seconds": [1]}})
        assert isinstance(folder.created_at, str)

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


class TestLinkListPagination:
    def test_has_more_read_from_nested_pagination_true(self):
        result = LinkList.model_validate(
            {"links": [], "pagination": {"limit": 20, "offset": 0, "hasMore": True}}
        )
        assert result.has_more is True
        assert result.limit == 20
        assert result.offset == 0

    def test_has_more_read_from_nested_pagination_false(self):
        result = LinkList.model_validate(
            {"links": [], "pagination": {"limit": 20, "offset": 40, "hasMore": False}}
        )
        assert result.has_more is False

    def test_top_level_has_more_key_is_not_used(self):
        """A stray top-level hasMore (not how the platform actually responds) must
        not be read — pagination.hasMore is the only source of truth."""
        result = LinkList.model_validate(
            {"links": [], "hasMore": True, "pagination": {"hasMore": False}}
        )
        assert result.has_more is False

    def test_missing_pagination_object_leaves_has_more_none(self):
        result = LinkList.model_validate({"links": []})
        assert result.has_more is None
