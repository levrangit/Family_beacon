from unittest.mock import Mock

from app.families import create_family


def test_create_family_calls_supabase_rpc():
    supabase_client = Mock()

    supabase_client.rpc.return_value.execute.return_value = Mock(
        data="family-123"
    )

    result = create_family(
        supabase_client=supabase_client,
        family_name="My Family",
    )

    supabase_client.rpc.assert_called_once_with(
        "create_family",
        {
            "family_name": "My Family",
        },
    )

    assert result == "family-123"


def test_create_family_rejects_empty_family_name():
    supabase_client = Mock()

    try:
        create_family(
            supabase_client=supabase_client,
            family_name="",
        )
    except ValueError as exc:
        assert str(exc) == "Family name is required"
    else:
        raise AssertionError("ValueError was not raised")

    supabase_client.rpc.assert_not_called()


def test_create_family_rejects_empty_supabase_result():
    supabase_client = Mock()

    supabase_client.rpc.return_value.execute.return_value = Mock(
        data=None
    )

    try:
        create_family(
            supabase_client=supabase_client,
            family_name="My Family",
        )
    except ValueError as exc:
        assert str(exc) == "Family ID was not returned"
    else:
        raise AssertionError("ValueError was not raised")
