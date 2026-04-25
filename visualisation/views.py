# Bokeh is a Python visualisation library that generates interactive charts
# components() splits a Bokeh plot into embeddable HTML and JavaScript
from bokeh.embed import components

# figure() creates a new Bokeh plot canvas to draw charts on
from bokeh.plotting import figure

# HoverTool adds an interactive hover effect when the mouse moves over bars
from bokeh.models import HoverTool
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

# Import models from the teams app — visualisation has no models of its own
# as it only reads and displays existing data
from teams.models import Department, Project, Team

# Only logged-in users can access this page
@login_required  
def visualisation_dashboard(request):
    """
    Display interactive Bokeh charts showing team, project and department data.
    Charts are generated server-side with Bokeh and embedded into the template.
    """

    # Use Django's annotate() to add a team_count field to each department
    departments = Department.objects.annotate(
        # This avoids multiple database queries — Count('teams') uses the
        # related_name defined in the Team model's ForeignKey to Department
        team_count=Count('teams')
    )

    # Builds the x-axis and y-axis data lists for Bokeh
    # Bokeh requires plain Python lists
    dept_names = [dept.department_name for dept in departments] # x-axis labels
    dept_counts = [dept.team_count for dept in departments] # y-axis values

    if not dept_names:
        dept_names = ['No departments']
        dept_counts = [0]

    plot1 = figure(
        # x_range sets the categorical x-axis labels
        x_range = dept_names,
        height=400,
        title='Number of Teams per Department',
        # toolbar_location=None and tools='' removes the default Bokeh toolbar
        toolbar_location=None,
        tools=''
    )

    # vbar() is used to draw vertical bars on the plot       
    plot1_vbar = plot1.vbar(
        x = dept_names,
        # top= sets the bar height (y-axis value)
        top = dept_counts,
        # width=0.5 means each bar takes up 50% of its allocated space
        width = 0.5,
        fill_color = 'steelblue',
        # alpha=0.8 sets the bar transparency (0=invisible, 1=fully opaque)
        alpha = 0.8,
        # hover_alpha=1 makes bars fully opaque when hovered over
        hover_alpha = 1
    )

    # HoverTool highlights a bar when the mouse moves over it   
    plot1.add_tools(HoverTool(
        # tooltips=None means no tooltip popup is shown, just the highlight effect
        tooltips = None,
        # renderers=[plot1_vbar] applies the hover only to the bars
        renderers = [plot1_vbar],
        mode='mouse'
    ))

    # Remove vertical grid lines
    plot1.xgrid.grid_line_color = None
    # By default Bokeh may not start bars at y=0 — this forces it to
    plot1.y_range.start = 0

    # Query the database to count teams by their status field
    # filter(status='active') uses the STATUS_CHOICES defined in the Team model
    active_count = Team.objects.filter(status='active').count()
    disabled_count = Team.objects.filter(status='disabled').count()

    # Build x-axis labels and y-axis values for the second chart
    statuses = ['Active', 'Disabled']
    status_counts = [active_count, disabled_count]

    # Create the second Bokeh figure for active vs disabled comparison
    plot2 = figure(
        x_range=statuses,
        height=400,
        title='Active vs Disabled Teams',
        toolbar_location=None,
        tools=''
    )

    # Create vertical bars with different colours per status
    plot2_vbar = plot2.vbar(
        x=statuses,
        top=status_counts,
        width=0.5,
        # A list of colours is passed to fill_color — one colour per bar
        # Green (#2ecc71) for active teams, red (#e74c3c) for disabled teams
        fill_color=['#2ecc71', '#e74c3c'],
        alpha=0.8,
        hover_alpha=1
    )

    # Add the same hover highlight effect to the second chart
    plot2.add_tools(HoverTool(
        tooltips=None,
        renderers=[plot2_vbar],
        mode='mouse'
    ))

    # Cleaning up the chart appearance
    plot2.xgrid.grid_line_color = None
    plot2.y_range.start = 0

    project_departments = Department.objects.annotate(
        project_count=Count('teams__projects', distinct=True)
    ).select_related('dept_head')

    project_dept_names = [dept.department_name for dept in project_departments] or ['No departments']
    project_counts = [dept.project_count for dept in project_departments] or [0]

    plot3 = figure(
        x_range=project_dept_names,
        height=400,
        title='Department Name vs Projects',
        toolbar_location=None,
        tools=''
    )

    plot3_vbar = plot3.vbar(
        x=project_dept_names,
        top=project_counts,
        width=0.5,
        fill_color='#0A3D93',
        alpha=0.85,
        hover_alpha=1
    )
    plot3.add_tools(HoverTool(
        tooltips=[('Department', '@x'), ('Projects', '@top')],
        renderers=[plot3_vbar],
        mode='mouse'
    ))
    plot3.xgrid.grid_line_color = None
    plot3.y_range.start = 0

    head_project_pairs = []
    for project in Project.objects.prefetch_related('teams__department__dept_head').order_by('name'):
        departments_for_project = {
            team.department for team in project.teams.all()
            if team.department_id
        }
        for department in departments_for_project:
            head_name = (
                department.dept_head.get_full_name() or department.dept_head.username
                if department.dept_head else 'No department head'
            )
            head_project_pairs.append((head_name, project.name))

    head_names = sorted({head for head, project_name in head_project_pairs}) or ['No department head']
    project_names = sorted({project_name for head, project_name in head_project_pairs}) or ['No projects recorded']
    head_values = [head for head, project_name in head_project_pairs] or ['No department head']
    project_values = [project_name for head, project_name in head_project_pairs] or ['No projects recorded']

    plot4 = figure(
        x_range=head_names,
        y_range=project_names,
        height=400,
        title='Department Head vs Project Name',
        toolbar_location=None,
        tools=''
    )
    plot4.scatter(
        x=head_values,
        y=project_values,
        size=12,
        fill_color='#2ecc71',
        line_color='#1f6b36',
        alpha=0.9,
    )
    plot4.add_tools(HoverTool(tooltips=[('Department head', '@x'), ('Project', '@y')]))
    plot4.xgrid.grid_line_color = None

    # components() splits each Bokeh plot into two parts:
    # - script: a <script> tag containing JavaScript to render the chart
    # - plot_html: a <div> tag that acts as the container for the chart
    # Both must be included in the template using the |safe filter
    # to prevent Django from escaping the HTML/JavaScript
    script1, plot1_html = components(plot1)
    script2, plot2_html = components(plot2)
    script3, plot3_html = components(plot3)
    script4, plot4_html = components(plot4)

    # Pass all chart components to the template via context
    context = {
        'script1':    script1,    # JavaScript for chart 1
        'plot1_html': plot1_html, # HTML div container for chart 1
        'script2':    script2,    # JavaScript for chart 2
        'plot2_html': plot2_html, # HTML div container for chart 2
        'script3': script3,
        'plot3_html': plot3_html,
        'script4': script4,
        'plot4_html': plot4_html,
    }
    return render(request, 'visualisation/visualisation.html', context)
