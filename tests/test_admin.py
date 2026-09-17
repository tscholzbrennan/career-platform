from app.services.admin_service import update_profile_summary


def test_admin_updates_profile_summary():
    result = update_profile_summary('Updated headline', 'Updated summary')
    assert result is not None
