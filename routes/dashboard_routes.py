# routes/dashboard_routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.project_model import get_projects_by_user
from models.boards_model import get_boards_by_project, get_tasks_by_board

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

@dashboard_bp.route('/')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session.get('username', 'User')
    
    # Get projects user is a member of
    projects = get_projects_by_user(user_id)

    # Task stats
    stats = {'To Do': 0, 'In Progress': 0, 'Review': 0, 'Done': 0}
    total_tasks = 0
    recent_tasks = []
    
    for project in projects:
        boards = get_boards_by_project(project['id'])
        for board in boards:
            tasks = get_tasks_by_board(board['id'])
            for status, task_list in tasks.items():
                stats[status] += len(task_list)
                total_tasks += len(task_list)
                # Collect recent tasks (limit to 5 most recent)
                for task in task_list[:2]:  # Get 2 from each status
                    task['project_name'] = project['name']
                    task['board_name'] = board['name']
                    recent_tasks.append(task)
    
    # Sort recent tasks by created_at and limit to 10
    recent_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    recent_tasks = recent_tasks[:10]
    
    # Calculate completion percentage
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = round((stats['Done'] / total_tasks) * 100, 1)

    return render_template(
        'dashboard/dashboard.html', 
        projects=projects, 
        stats=stats,
        total_tasks=total_tasks,
        completion_rate=completion_rate,
        recent_tasks=recent_tasks,
        username=username
    )