from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from teams.models import Department, Dependency, Organisation, Team, TeamType


class Command(BaseCommand):
    help = "Create idempotent Student 2 demo data for organisations, departments, team types and dependencies."

    def handle(self, *args, **options):
        User = get_user_model()

        def create_user(username, first_name, last_name, email, password=None):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                },
            )
            if password:
                user.set_password(password)
                user.save()
            elif created:
                user.set_unusable_password()
                user.save()
            return user

        create_user(
            "student2_demo",
            "Student",
            "Two",
            "student2_demo@example.com",
            password="Student2Demo123!",
        )

        organisation, _ = Organisation.objects.update_or_create(
            organisation_name="Sky Engineering",
            defaults={
                "organisation_description": "Central engineering organisation for Sky's internal team directory demo.",
            },
        )

        team_types = {}
        for name, description in [
            ("Platform", "Teams that run shared engineering platforms and services."),
            ("Product", "Teams that build customer-facing or colleague-facing product features."),
            ("Operations", "Teams focused on reliability, support and operational readiness."),
        ]:
            team_types[name], _ = TeamType.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )

        platform_head = create_user("platform_head", "Priya", "Shah", "platform_head@example.com")
        product_head = create_user("product_head", "Daniel", "Morgan", "product_head@example.com")

        platform_dept, _ = Department.objects.update_or_create(
            department_name="Platform Engineering",
            defaults={
                "department_description": "Owns shared services, deployment tooling and core APIs.",
                "department_location": "Osterley",
                "specialisation": "Cloud platforms and backend services",
                "organisation": organisation,
                "dept_head": platform_head,
            },
        )

        product_dept, _ = Department.objects.update_or_create(
            department_name="Product Engineering",
            defaults={
                "department_description": "Builds digital product journeys for web and mobile users.",
                "department_location": "Leeds",
                "specialisation": "Customer product delivery",
                "organisation": organisation,
                "dept_head": product_head,
            },
        )

        team_specs = [
            ("Core APIs", platform_dept, "Platform", "Provides reusable backend APIs for product teams."),
            ("Identity Services", platform_dept, "Platform", "Owns authentication and account services."),
            ("Platform Operations", platform_dept, "Operations", "Supports deployment, monitoring and incident response."),
            ("Frontend Web", product_dept, "Product", "Builds the main web experience."),
            ("Mobile Apps", product_dept, "Product", "Builds iOS and Android product features."),
            ("Customer Support Tools", product_dept, "Product", "Builds internal support tooling for customer operations."),
        ]

        teams = {}
        for index, (name, department, type_name, description) in enumerate(team_specs, start=1):
            manager = create_user(
                f"manager_{index}",
                f"Manager{index}",
                "Demo",
                f"manager_{index}@example.com",
            )
            team, _ = Team.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "department": department,
                    "manager": manager,
                    "team_type": team_types[type_name],
                    "status": "active",
                },
            )

            members = [
                create_user(
                    f"{name.lower().replace(' ', '_')}_member_{member_index}",
                    f"Member{member_index}",
                    name.replace(" ", ""),
                    f"{name.lower().replace(' ', '_')}_member_{member_index}@example.com",
                )
                for member_index in range(1, 6)
            ]
            team.members.set(members)
            teams[name] = team

        dependencies = [
            ("Frontend Web", "Core APIs", "API"),
            ("Mobile Apps", "Core APIs", "API"),
            ("Customer Support Tools", "Identity Services", "Authentication"),
            ("Core APIs", "Identity Services", "Authentication"),
            ("Core APIs", "Platform Operations", "Operational support"),
            ("Mobile Apps", "Platform Operations", "Release support"),
        ]

        for downstream, upstream, dependency_type in dependencies:
            Dependency.objects.update_or_create(
                team=teams[downstream],
                depends_on=teams[upstream],
                defaults={"dependency_type": dependency_type},
            )

        self.stdout.write(self.style.SUCCESS(
            "Student 2 demo data ready: 1 organisation, 2 departments, 6 teams, 3 team types and 6 dependencies."
        ))
        self.stdout.write("Demo login: student2_demo / Student2Demo123!")
