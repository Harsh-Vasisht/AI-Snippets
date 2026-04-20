# app/cli/tasks_cli.py
import click
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task, PriorityEnum, CategoryEnum

@click.group()
def task_cli():
    pass

@task_cli.command()
@click.option("--title", prompt="Task title")
@click.option("--description", prompt="Task description", default="")
@click.option("--priority", type=click.Choice([p.value for p in PriorityEnum]), default="Medium")
@click.option("--category", type=click.Choice([c.value for c in CategoryEnum]), default="Misc")
@click.option("--owner-id", type=int, prompt="Owner User ID")
def add(title, description, priority, category, owner_id):
    """Add a new task with priority and category"""
    db: Session = get_db()
    new_task = Task(title=title, description=description, priority=priority, category=category, owner_id=owner_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    click.echo(f"Task '{title}' added with priority {priority} and category {category}")

@task_cli.command()
@click.option("--filter-priority", type=click.Choice([p.value for p in PriorityEnum]), default=None)
@click.option("--filter-category", type=click.Choice([c.value for c in CategoryEnum]), default=None)
def list_tasks(filter_priority, filter_category):
    """List tasks with optional priority/category filtering"""
    db: Session = get_db()
    query = db.query(Task)
    if filter_priority:
        query = query.filter(Task.priority == filter_priority)
    if filter_category:
        query = query.filter(Task.category == filter_category)
    tasks = query.all()
    for task in tasks:
        click.echo(f"[{task.priority}/{task.category}] {task.title} (ID: {task.id})")
