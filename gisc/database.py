#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Database configuration and query APIs."""


import pymongo

from errors import DBCollNameError

__author__ = "anshu.choubey@imaginea.com"


class DBConfiguration(object):
    """Database configuration APIs"""
    client = pymongo.MongoClient()

    def __init__(self, db_name=None):
        """Initiate database configuration.

        :Parameters:
            - db_name : str : Name of the database. Defaults to None.
        """
        self.db_name = db_name

    def db_obj(self, db_name=None):
        """Connect to a database.

        :Parameters:
            - db_name : str : Name of the database. Defaults to None.
        :Raises:
            - DBCollNameError when parameter db_name is not of
            str or unicode.
        :Returns:
            - db_obj : pymongo.database.Database object : Database
            connection object.
        """
        if not db_name:
            db_name = self.db_name
        try:
            db_obj = self.client[self.db_name]
        except TypeError:
            raise DBCollNameError('INVALID_TYPE', db_name)
        return db_obj

    def all_db(self):
        """Returns names of all the databases."""
        return self.client.database_names()

    def drop_db(self, db_name=None):
        """Drop a database.

        :Parameters:
            - db_name : str : Name of the database. Defaults to None.
        :Raises:
            - DBCollNameError when parameter db_name is not of
            str or unicode.
        """
        if not db_name:
            db_name = self.db_name
        try:
            self.client.drop_database(db_name)
        except TypeError:
            raise DBCollNameError('INVALID_TYPE', db_name)

    def drop_all_db(self):
        """Drop every mongo database."""
        for db_obj in self.all_db():
            self.drop_db(db_obj)

    def coll(self, coll_name, db_name=None):
        """Get a particular collection of a database.

        :Parameters:
            - coll_name : str : Name of the collection to connect to.
            - db_name : str : Name of the database. Defaults to None.
        :Raises:
            - DBCollNameError when parameter coll_name is not of
            str or unicode.
        :Returns:
            - coll : pymongo.collection.Collection object : A mongo
            collection object.
        """
        db_obj = self.db_obj(db_name)
        try:
            coll = db_obj[coll_name]
        except TypeError:
            raise DBCollNameError('INVALID_TYPE', coll_name)
        return coll

    def all_coll(self, db_name=None):
        """Get all collections of a database.

        :Parameters:
            - db_name : str : Name of the database. Defaults to None.
        :Returns:
            - list : All collection names of the database.
        """
        db_obj = self.db_obj(db_name)
        return db_obj.collection_names()

    def drop_coll(self, coll_name, db_name=None):
        """Drop a collection of a database.

        :Parameters:
            - coll_name : str : Name of the collection to drop.
            - db_name : str : Name of the database to drop from.
            Defaults to None.
        :Raises:
            - DBCollNameError when parameter coll_name is not of
            str or unicode.
        """
        db_obj = self.db_obj(db_name)
        try:
            db_obj.drop_collection(coll_name)
        except TypeError:
            raise DBCollNameError('INVALID_TYPE', coll_name)

    def drop_all_coll(self, db_name=None):
        """Drop every collection of a database."""
        db_obj = self.db_obj(db_name)
        for coll in self.all_coll(db_obj):
            self.drop_coll(coll, db_obj)


def _match(q_dict):
    """Construct the match query.

    :Parameters:
        - q_dict : dict : mapping of fields and their values to be
        performed as part of the match query.
    :Returns:
        - dict : The fields and values mapped in the match query
        skeleton.
    """
    match = {}
    match.update(q_dict)
    return {'$match': match}


def _group(q_dict):
    """Construct the grouping query.

    :Parameters:
        - q_dict : dict : mapping of fields and their values to be
        performed as part of the group query.
    :Returns:
        - dict : The fields and values mapped in the group query
        skeleton.
    """
    group = {}
    group.update(q_dict)
    return {'$group': group}


def _project(q_dict):
    """Construct the projection query.

    :Parameters:
        - q_dict : dict : mapping of fields and their values to be
        performed as part of the project query.
    :Returns:
        - dict : The fields and values mapped in the project query
        skeleton.
    """
    project = {}
    project.update(q_dict)
    return {'$project': project}


def _sort(q_dict):
    """Construct the sort query.

    :Parameters:
        - q_dict : dict : mapping of fields and their values to be
        performed as part of the sort query.
    :Returns:
        - dict : The fields and values mapped in the sort query
        skeleton.
    """
    sort = {}
    sort.update(q_dict)
    return {'$sort': sort}


def _unwind(q_dict):
    """Construct the match query.

    :Parameters:
        - q_dict : dict : mapping of fields and their values to be
        performed as part of the match query.
    :Returns:
        - dict : The fields and values mapped in the match query
        skeleton.
    """
    unwind = {}
    unwind.update(q_dict)
    return {'$unwind': unwind}


class Query(object):
    """Database querying APIs"""
    def __init__(self, db_name):
        """Establish the database connection and configure the database
        object.

        :Parameters:
            - db_name : str : Name of the database to connect.
        """
        self.db_config = DBConfiguration(db_name)

    def get_repo_lang(self, coll):
        """Get every repository language in the database.

        :Parameters:
            - coll : str : Name of the collection to look inside.
        :Returns:
            - list : Sequence of distinct repository languages.
        """
        coll = self.db_config.coll(coll)
        return coll.distinct('repository.language')

    def get_high_profile_users(self, coll):
        """Get users with their followers in descending order.

        :Parameters:
            - coll : str : Name of the collection to look inside.
        :Returns:
            - list : Sequence of mappings of users and their followers
            organised in a descending order.
        """
        coll = self.db_config.coll(coll)
        return coll.aggregate([
            {'$group': {'_id': '$payload.target.login',
                        'followers': {'$max': '$payload.target.followers'},
                        }
             },
            {'$sort': {'followers': pymongo.DESCENDING}},
        ])['result']

    def get_user_watch_events(self, coll, match):
        """Get users with their followers in descending order.

        :Parameters:
            - coll : str : Name of the collection to look inside.
            - match : dict : Mapping of the field and value to look for
            match query.
        :Returns:
            - list : Sequence of mappings of a user's watch events.
        """
        coll = self.db_config.coll(coll)
        return coll.aggregate([
            _match(match),
            {'$group': {'_id': '$repository.url',
                        'created_at': {'$min': '$created_at'},
                        'watchers': {'$first': '$repository.watchers'},
                        },
             },
        ])['result']

    def get_followers_count(self, coll, match):
        """Get users with their followers in descending order.

        :Parameters:
            - coll : str : Name of the collection to look inside.
            - match : dict : Mapping of the field and value to look for
            match query.
        :Returns:
            - int : Number of followers for a particular user.
        """
        coll = self.db_config.coll(coll)
        return coll.aggregate([
            _match(match),
            {'$group': {'_id': None,
                        'followers': {'$max': '$payload.target.followers'}
                        },
             },
        ])['result'][0]['followers']

    def get_repo_watchers(self, coll, match):
        """Get the watchers count of a repository.

        :Parameters:
            - coll : str : Name of the collection to look inside.
            - match : dict : Mapping of the field and value to look for
            match query.
        :Returns:
            - list : Sequence of mappings of a repo's event time and
            maximum watcher at the moment.
        """
        coll = self.db_config.coll(coll)
        return coll.aggregate([
            _match(match),
            {'$group': {'_id': '$created_at',
                        'watchers': {'$max': '$repository.watchers'},
                        },
             },
            {'$sort': {'_id': pymongo.ASCENDING}},
        ])['result']

    def get_repo_watchers_at_time_limit(self, coll, match):
        """Get the watchers count of a repository before a time span.

        :Parameters:
            - coll : str : Name of the collection to look inside.
            - match : dict : Mapping of the field and value to look for
            match query.
        :Returns:
            - int : Count of a repo's watchers just before a timestamp.
        """
        coll = self.db_config.coll(coll)
        return coll.aggregate([
            _match(match),
            {'$group': {'_id': '$repository.url',
                        'watchers': {'$last': '$repository.watchers'},
                        },
             },
        ])['result'][0]['watchers']
