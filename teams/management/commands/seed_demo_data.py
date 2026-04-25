from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_messages_practice.messages_app.models import Message as PortalMessage
from teams.models import (
    ContactChannel,
    Department,
    Dependency,
    Meeting,
    Organisation,
    Project,
    Repository,
    Skill,
    Team,
    TeamType,
)


class Command(BaseCommand):
    help = "Create repeatable demo data for the full Sky Engineering coursework application."

    def handle(self, *args, **options):
        User = get_user_model()

        def user(username, first_name, last_name, email, password=None, staff=False):
            obj, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_staff": staff,
                    "is_superuser": staff,
                },
            )
            changed = False
            for field, value in {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "is_staff": staff,
                "is_superuser": staff,
            }.items():
                if getattr(obj, field) != value:
                    setattr(obj, field, value)
                    changed = True
            if password:
                obj.set_password(password)
                changed = True
            elif created:
                obj.set_unusable_password()
                changed = True
            if changed:
                obj.save()
            return obj

        demo_user = user(
            "student_demo",
            "Student",
            "Demo",
            "student_demo@example.com",
            password="StudentDemo123!",
        )
        admin_user = user(
            "admin_demo",
            "Admin",
            "Demo",
            "admin_demo@example.com",
            password="AdminDemo123!",
            staff=True,
        )

        organisation, _ = Organisation.objects.update_or_create(
            organisation_name="Sky Engineering",
            defaults={"organisation_description": "Demo organisation for the engineering team portal."},
        )

        type_data = {
            "Platform": "Shared platforms, infrastructure and APIs.",
            "Product": "Customer and colleague-facing product delivery.",
            "Operations": "Reliability, release and support operations.",
        }
        team_types = {
            name: TeamType.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )[0]
            for name, description in type_data.items()
        }

        platform_head = user("sebastian_holt", "Sebastian", "Holt", "sebastian.holt@example.com")
        product_head = user("amelia_wright", "Amelia", "Wright", "amelia.wright@example.com")

        platform_dept, _ = Department.objects.update_or_create(
            department_name="xTV Web",
            defaults={
                "department_description": "Web platform teams adapted from the Sky registry sample.",
                "department_location": "Osterley",
                "specialisation": "Web platforms and shared services",
                "organisation": organisation,
                "dept_head": platform_head,
            },
        )
        product_dept, _ = Department.objects.update_or_create(
            department_name="Customer Products",
            defaults={
                "department_description": "Teams delivering product journeys and support tooling.",
                "department_location": "Leeds",
                "specialisation": "Customer product delivery",
                "organisation": organisation,
                "dept_head": product_head,
            },
        )

        team_specs = [
            ("Code Warriors", platform_dept, "Platform", "Infrastructure scalability, CI/CD integration and platform resilience.", "Olivia", "Carter"),
            ("The Debuggers", platform_dept, "Platform", "Advanced debugging tools and automated error detection.", "James", "Bennett"),
            ("Bit Masters", platform_dept, "Operations", "Security compliance, encryption techniques and data integrity.", "Emma", "Richardson"),
            ("Frontend Development", product_dept, "Product", "Web customer journeys and front-end feature delivery.", "Benjamin", "Hayes"),
            ("Mobile Apps", product_dept, "Product", "iOS and Android product features.", "Sophia", "Mitchell"),
            ("Customer Support Tools", product_dept, "Product", "Internal tools for customer operations.", "", ""),
        ]

        teams = {}
        for index, (name, department, type_name, description, first_name, last_name) in enumerate(team_specs, 1):
            manager = None
            if first_name:
                manager = user(
                    f"{first_name.lower()}_{last_name.lower()}",
                    first_name,
                    last_name,
                    f"{first_name.lower()}.{last_name.lower()}@example.com",
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
                user(
                    f"{name.lower().replace(' ', '_')}_member_{member_index}",
                    f"Member{member_index}",
                    name.replace(" ", ""),
                    f"{name.lower().replace(' ', '_')}_member_{member_index}@example.com",
                )
                for member_index in range(1, 6)
            ]
            team.members.set(members)
            teams[name] = team

        skill_data = {
            "Code Warriors": ["AWS", "Terraform", "Kubernetes", "CI/CD", "Docker"],
            "The Debuggers": ["Debugging", "Log Analysis", "Python", "Java", "Root Cause Analysis"],
            "Bit Masters": ["Cryptography", "Security Compliance", "Penetration Testing"],
            "Frontend Development": ["JavaScript", "Django Templates", "Accessibility"],
            "Mobile Apps": ["iOS", "Android", "Release Management"],
            "Customer Support Tools": ["CRM", "Internal Tools", "SQL"],
        }
        for team_name, skills in skill_data.items():
            for skill_name in skills:
                Skill.objects.get_or_create(team=teams[team_name], name=skill_name)

        for team_name, team in teams.items():
            Repository.objects.update_or_create(
                team=team,
                name=f"{team_name} Repository",
                defaults={
                    "url": f"https://example.com/repos/{team_name.lower().replace(' ', '-')}",
                    "description": f"Demo repository for {team_name}.",
                },
            )
            ContactChannel.objects.get_or_create(
                team=team,
                channel_type="slack",
                channel_value=f"#{team_name.lower().replace(' ', '-')}",
            )
            ContactChannel.objects.get_or_create(
                team=team,
                channel_type="email",
                channel_value=f"{team_name.lower().replace(' ', '.')}@example.com",
            )

        dependency_data = [
            ("The Debuggers", "Code Warriors", "Infrastructure Support"),
            ("Bit Masters", "The Debuggers", "Security Fixes"),
            ("Frontend Development", "Code Warriors", "API"),
            ("Mobile Apps", "Code Warriors", "API"),
            ("Customer Support Tools", "Frontend Development", "Internal Tooling"),
            ("Code Warriors", "Bit Masters", "Security Review"),
        ]
        for downstream, upstream, dependency_type in dependency_data:
            Dependency.objects.update_or_create(
                team=teams[downstream],
                depends_on=teams[upstream],
                defaults={"dependency_type": dependency_type},
            )

        project_specs = [
            ("Client Lightning Xtv", "active", ["Code Warriors", "The Debuggers", "Bit Masters"]),
            ("Customer App Refresh", "active", ["Frontend Development", "Mobile Apps"]),
            ("Support Console Upgrade", "planned", ["Customer Support Tools", "Frontend Development"]),
        ]
        for project_name, status, project_teams in project_specs:
            project, _ = Project.objects.update_or_create(
                name=project_name,
                defaults={
                    "description": f"Demo project: {project_name}.",
                    "status": status,
                },
            )
            project.teams.set([teams[name] for name in project_teams])

        meeting_times = [
            ("Platform Dependency Review", "teams", teams["Code Warriors"], 3),
            ("Mobile Release Planning", "zoom", teams["Mobile Apps"], 7),
            ("Support Tools Backlog", "google_meet", teams["Customer Support Tools"], 10),
        ]
        for title, platform, team, day_offset in meeting_times:
            scheduled_at = timezone.now() + timezone.timedelta(days=day_offset)
            meeting, _ = Meeting.objects.update_or_create(
                title=title,
                defaults={
                    "organiser": demo_user,
                    "team": team,
                    "platform": platform,
                    "scheduled_at": scheduled_at,
                    "message": f"Agenda for {title}.",
                },
            )
            meeting.attendees.set(team.members.all()[:3])

        PortalMessage.objects.update_or_create(
            subject="Dependency review notes",
            defaults={
                "recipient": "Code Warriors",
                "body": "Please review downstream dependency updates before the next standup.",
                "is_draft": False,
            },
        )
        PortalMessage.objects.update_or_create(
            subject="Draft release message",
            defaults={
                "recipient": "Mobile Apps",
                "body": "Draft message for the upcoming mobile release.",
                "is_draft": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Full demo data is ready."))
        self.stdout.write("User login: student_demo / StudentDemo123!")
        self.stdout.write("Admin login: admin_demo / AdminDemo123!")
