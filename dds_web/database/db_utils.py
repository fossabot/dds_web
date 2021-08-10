""" Utility function that makes DB calls """

from dds_web import db, app
from dds_web.database import models
from sqlalchemy import func
import sqlalchemy


def get_facility_column(fid, column) -> (str):
    """Gets the columns value from DB for given facility ID"""
    facility = models.Facility.query.filter_by(id=fid).first()
    return getattr(facility, column)


def get_facility_column_by_username(fname, column) -> (str):
    """Gets the columns value from DB for given facility username"""
    facility = models.Facility.query.filter_by(username=fname).first()
    return getattr(facility, column)


def get_facilty_projects(facility_id) -> (list):
    """Gets all the project for the facility ID"""

    # Get all projects connected to facility
    try:
        project_list = models.Project.query.filter_by(facility_id=facility_id).all()
    except sqlalchemy.exc.SQLAlchemyError:
        raise

    if not project_list:
        project_list = []

    return project_list


def get_user_column_by_username(username, column) -> (str):
    """Gets the columns value from DB for given username"""
    user = models.User.query.filter_by(username=username).first()
    return getattr(user, column)


def get_user_projects(current_user) -> (list):
    """Gets all the project for the username ID"""

    # Join Project and association table and get user projects
    try:
        projects = (
            models.Project.query.join(models.project_users)
            .filter(
                (models.project_users.c.project_id == models.Project.id)
                & (models.project_users.c.user == current_user)
            )
            .all()
        )
    except sqlalchemy.exc.SQLAlchemyError:
        raise

    if not projects:
        projects = []

    return projects


def get_project_users(project_id, no_facility_users=False) -> (list, list):
    """Get list of users related to the project"""

    # project_users = []
    try:
        users = (
            models.User.query.join(models.project_users)
            .filter(
                (models.project_users.c.user == models.User.username)
                & (models.project_users.c.project_id == project_id)
            )
            .all()
        )
        # project_users = (
        #     db.session.query(models.project_users)
        #     .filter_by(project_id=project_id)
        #     .with_entities(models.project_users.c.user)
        #     .all()
        # )
    except sqlalchemy.exc.SQLAlchemyError:
        raise

    app.logger.debug(users)
    # for row in project_user_rows:
    #     user = models.User.query.filter_by(id=row.user_id).one()
    #     if no_facility_users and (user.role != "researcher"):
    #         continue
    #     project_users.append(user.username)
    return [user.username for user in users]


def get_full_column_from_table(table, column) -> (list):
    """Get the whole column from the given table"""
    mtable = getattr(models, table)
    return [entry[0] for entry in mtable.query.with_entities(getattr(mtable, column)).all()]
