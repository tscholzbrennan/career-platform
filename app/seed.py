from sqlalchemy.orm import Session

from app.models import Profile, Project, Experience


def seed_data(db: Session) -> None:
    if db.query(Profile).first() is None:
        db.add(
            Profile(
                headline="Data & AI Engineer building practical analytics products",
                summary=(
                    "I design and ship data-driven products that turn messy information into clear decisions. "
                    "My work blends analytics, experimentation, and product thinking to help teams move from raw data to measurable outcomes."
                ),
                location="Remote",
                email="hello@example.com",
                linkedin_url="https://www.linkedin.com",
                github_url="https://github.com",
                resume_url="/resume",
                profile_image="",
                focus_area="Data & AI",
            )
        )

    if db.query(Project).first() is None:
        db.add(
            Project(
                title="Demand Forecasting Dashboard",
                slug="demand-forecasting-dashboard",
                summary="Forecasted business demand and built executive reporting for a fast-moving team.",
                description="Designed and built a forecasting workflow that cleaned regional sales data, surfaced demand signals, and enabled product teams to plan with confidence.",
                role="Data Analyst / Product Analyst",
                tech_stack=["Python", "SQL", "SQLite", "Charting"],
                tags=["analytics", "forecasting", "dashboard"],
                repo_url="https://github.com",
                demo_url="/projects/demand-forecasting-dashboard",
                metrics=["Reduced reporting time by 50%", "Improved forecast coverage across 3 regions"],
                case_study="Built a repeatable data pipeline and a stakeholder-facing dashboard that made forecast visibility consistent across teams.",
                featured=1,
            )
        )
        db.add(
            Project(
                title="AI Research Briefing Tool",
                slug="ai-research-briefing-tool",
                summary="Turned fragmented research notes into structured briefs for product and strategy decisions.",
                description="Created a lightweight workflow for collecting source material, extracting key themes, and generating structured summaries for stakeholder review.",
                role="AI Product Builder",
                tech_stack=["Python", "FastAPI", "LLM", "SQLite"],
                tags=["ai", "research", "ux"],
                repo_url="https://github.com",
                demo_url="/projects/ai-research-briefing-tool",
                metrics=["Reduced synthesis time by 40%", "Standardized outputs for leadership reviews"],
                case_study="The tool gave the research team a consistent way to transform raw inputs into decision-ready briefs.",
                featured=1,
            )
        )

    if db.query(Experience).first() is None:
        db.add(
            Experience(
                role_title="Data Analyst",
                company_name="Example Company",
                start_date="2023-01",
                end_date="2024-06",
                location="Remote",
                summary="Worked with cross-functional teams to improve reporting, instrumentation, and decision support.",
                bullet_points=[
                    "Built dashboards and insights for product and revenue teams.",
                    "Improved data quality tracking for operational reporting.",
                    "Partnered with engineering to define key metrics and KPIs."
                ],
                impact_notes=["Improved visibility into conversion and retention trends.", "Accelerated weekly reporting cycles."],
                skills=["SQL", "Python", "Analytics", "Stakeholder Communication"],
            )
        )

    db.commit()
