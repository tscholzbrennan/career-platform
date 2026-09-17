from app.services.fallback_profile import load_fallback_profile


def test_fallback_loads_snapshot():
    data = load_fallback_profile()
    assert 'headline' in data
    assert 'contact_links' in data
    assert data['source'] == 'fallback'
