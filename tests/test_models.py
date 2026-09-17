from app.models import Profile, Experience, Project


def test_models_exist():
    assert Profile.__tablename__ == 'profiles'
    assert Experience.__tablename__ == 'experiences'
    assert Project.__tablename__ == 'projects'
