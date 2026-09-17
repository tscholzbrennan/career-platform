from sqlalchemy import Column, Integer, String, Text, JSON, Date
from app.db import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    location = Column(String(255), default="Remote")
    email = Column(String(255), nullable=False)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    resume_url = Column(String(255), nullable=True)
    profile_image = Column(String(255), nullable=True)
    focus_area = Column(String(255), default="Data & AI")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    role_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=False)
    bullet_points = Column(JSON, default=list)
    impact_notes = Column(JSON, default=list)
    skills = Column(JSON, default=list)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    role = Column(String(255), nullable=False)
    tech_stack = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    repo_url = Column(String(255), nullable=True)
    demo_url = Column(String(255), nullable=True)
    metrics = Column(JSON, default=list)
    case_study = Column(Text, nullable=True)
    featured = Column(Integer, default=0)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    proficiency = Column(String(255), nullable=True)


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    dates = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    media_type = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)


class FallbackProfileSnapshot(Base):
    __tablename__ = "fallback_profile_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    contact_links = Column(JSON, nullable=False)
    featured_projects = Column(JSON, nullable=False)
    resume_url = Column(String(255), nullable=True)
    last_sync = Column(Date, nullable=True)
    source_of_truth = Column(String(50), default="fallback")
