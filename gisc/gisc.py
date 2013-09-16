#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""GISC related APIs.

APIs to manipulate user dynamics and events co-relations by querying
database and producing their plots to understand the trends followed
by other users for repositories and miscellaneous details.
The module takes flagged input from the bash shell. The flags represent
parameters to filter results on and could be one of the followings:-

    1. Repository language to filter on.
    2. Count of objects to be considered for the analysis.
    3. Directory to plot the results.
    4. Image extension for the graph.

For more on the flags, run the script with -h flag.
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pylab as plb

try:
    import warnings
    warnings.simplefilter('ignore', np.RankWarning)
except ImportError:
    pass

from database import Query
from errors import (DefaultArgInvalidValError, GISCError, InvalidLanguageError)
import gisc_msgs
from log import CLOG, FLOG, set_logs_dir
import utils

__author__ = "anshu.choubey@imaginea.com"

# Global Query object.
Q = None


def configure(db_name):
    """Globally configure database to perform queries.

    :Parameters:
        - db_name : str : Name of the database to configure.
    """
    global Q
    Q = Query(db_name)
    CLOG.info(gisc_msgs.DB_CONFIG_STMNT % db_name)


configure(gisc_msgs.GISC_DB)


def get_growth(repo_all_events):
    """Get co-ordinate values for actual growth curve.

    :Parameters:
        - repo_all_events : list : Sequence of mappings of a repo's
        event time and maximum watcher at the moment.
    :Returns:
        - numpy.ndarray object : Float value of time stamp for events,
        for x axis.
        - numpy.ndarray object : Watchers at the time stamp, for y axis.
    """
    x_tstamp, y_tstamp = [], []
    for event in repo_all_events:
        event_created_at = event['_id']
        x_tstamp.append(utils.get_float_time(event_created_at))
        y_tstamp.append(event['watchers'])
    return np.array(x_tstamp), np.array(y_tstamp)


def get_predict(x_tstamp, y_tstamp, event_created_at):
    """Get co-ordinate values for predicted curve.

    :Parameters:
        - x_tstamp : numpy.ndarray object : Float value of time stamp
        for events, for x axis.
        - y_tstamp : numpy.ndarray object : Watchers at the time stamp,
        for y axis.
        - event_created_at : float : Event creation time stamp value.
    :Returns:
        - x_pred : numpy.ndarray object : Float value of time stamp for
        events starting from the event creation time, for x axis.
        - y_pred : numpy.ndarray object : Value obtained after fitting
        watchers count in the 2nd degree polynomial function obtained
        from the x_tstamp and the y_tstamp values, for y axis.
    """
    x_pred = np.linspace(event_created_at, x_tstamp.max())
    y_pred = np.polyval(np.polyfit(x_tstamp, y_tstamp, 2), x_pred)
    return x_pred, y_pred


def is_eligible(y_tstamp, y_pred):
    """Check if a graph is eligible to be drawn.

    :Parameters:
        - y_tstamp : numpy.ndarray object : Watchers at the time stamp.
        - y_pred : numpy.ndarray object : Predicted value for watchers.
    :Returns:
        - Boolean : True if absolute value of difference between the
        two counts is greater than 10.
    """
    effect = 0
    for actual, pred in zip(y_tstamp, y_pred):
        effect += actual - pred
    return abs(effect) > 10


def get_set_user_impact_on_repos(user, followers, user_watched_repo, lang,
                                 user_watch_impact):
    """Get deviation due to impact of user watch event.

    :Parameters:
        - user : str : User whose impact is to be studied.
        - followers : int : Follower count for the user.
        - user_watched_repo : dict : Mapping of users and their watched
        repositories.
        - lang : str : Desired repository language.
        - user_watch_impact : dict : Mapping of user and its impact on
        repositories.
    :Returns:
        - std : numpy.float64 : Deviation value of the user effect on.
    """
    user_impact = user_watch_impact.get(user)
    if user_impact:
        return user_impact
    user_impact = []
    for watch in user_watched_repo[user]:
        repo, event_created_at, watchers = \
            watch['_id'], watch['created_at'], watch['watchers']
        time_limit = utils.get_24_hrs_hence_datetime_str(event_created_at)
        time_limit = time_limit.replace('-', '/') + ' '
        match = {'repository.url': repo, 'created_at': {'$lte': time_limit}}
        if lang:
            match['repository.language'] = lang
        limit_watchers = Q.get_repo_watchers_at_time_limit(gisc_msgs.ALL_COLL,
                                                           match)
        diff = limit_watchers - watchers
        if diff > 50:
            user_impact.append(diff * followers)
    std = 1000
    if len(user_impact) > 1:
        std = np.std(user_impact)
    user_watch_impact[user] = std
    return std


def plot_curve(plot_dir, user, repo, x_tstamp, y_tstamp, fevent_created_at,
               ftime_limit, x_pred, y_pred, lang, img_fmt):
    """Plot curve for a user watch impact on a repository.

    :Parameters:
        - plot_dir : str : Path where plot is to be generated.
        - user : str : User whose impact is to be studied.
        - repo : str : URL of the repository being plotted.
        - x_tstamp : numpy.ndarray object : Float value of time stamps
        for events, for x axis.
        - y_tstamp : numpy.ndarray object : Watchers at time stamps,
        for y axis.
        - fevent_created_at : float : Value of the time stamp when the
        event was created.
        - ftime_limit : float : Value of the time stamp 24 hours hence
        the event was created.
        - x_pred : numpy.ndarray object : Time stamp during the window
        between event creation to 24 hours hence time.
        - y_pred : numpy.ndarray object : Predicted value for watchers.
        - lang : str : Desired repository language.
        - img_fmt : str : Desired plot file extension.
    """
    plt.plot(x_tstamp, y_tstamp, marker='o')
    plt.plot(x_pred, y_pred, '--')
    xlabel = [user, '-->', repo]
    if lang:
        xlabel = [lang, ':'] + xlabel
    plt.xlabel(' '.join(xlabel), fontsize=10)
    plt.axvline(
        fevent_created_at, color='r', linestyle='dashed', linewidth=0.5)
    plt.axvline(ftime_limit, color='r', linestyle='dashed', linewidth=0.5)
    plt.legend(['Actual', 'Predicted', 'Impact Start', 'Impact End'],
               loc='upper left')
    plot_dir = os.path.abspath(plot_dir) + os.sep
    if lang:
        file_name = [plot_dir,
                     lang, ':',
                     user, ':', repo[repo.rfind('/') + 1:], '.', img_fmt]
    else:
        file_name = [plot_dir,
                     user, ':', repo[repo.rfind('/') + 1:], '.', img_fmt]
    plb.savefig(''.join(file_name))
    plt.close()


def high_profile_user_watch_events(lang, count):
    """Get watch events for the users.

    :Parameters:
        - lang : str : Repository language if needs to be filtered on.
        - count : int : Count limit of high profile users to get their
        watch events.
    :Returns:
        - user_watched_repo : dict : Mapping of users and their watch
        details.
    """
    follow_obj = Q.get_high_profile_users(gisc_msgs.FOLLOW_COLL)
    user_watched_repo = {}
    for i, follow in enumerate(follow_obj):
        if count and i == count:
            break
        user = follow['_id']
#         if not user in _TEST_USERS:
#             continue
        match = {'actor': user}
        if lang:
            match['repository.language'] = lang
        watch_events = Q.get_user_watch_events(gisc_msgs.WATCH_COLL, match)
        if not len(watch_events):
            FLOG.info(gisc_msgs.NO_WATCH_DEBUG % user)
            continue
        user_watched_repo[user] = watch_events
    return user_watched_repo


def get_language(lang):
    """Transform user input language into database stored language.

    :Parameters:
        - lang : str : Language input by user.
    :Raises:
        - InvalidLanguageError if the user input language is unknown.
    :Returns:
        - str : Transformed language as in the database.
    """
    _langs = Q.get_repo_lang(gisc_msgs.ALL_COLL)
    _langs = {i.lower(): i for i in _langs}
    try:
        return _langs[lang.lower()]
    except KeyError:
        raise InvalidLanguageError('INVALID_LANG', lang)


def high_profile_user_watch_effect(lang=None, count=None, plot_dir=None,
                                   logs_dir=None, img_fmt='png'):
    """Plot high profile user watch event impact on any repository.

    Assess the effect of watch event of a high profile user on a repo.
    Do people tend to be active on the repository being watched by any
    user with more number of users. The behaviour is then plotted for
    significant outcomes.
    :Parameters:
        - lang : str : Language input by user.
        - count : int : Count limit of high profile users to get their
        watch events.
        - plot_dir : str : Path where plot is to be generated. The path
        is deleted and created again.
        - logs_dir : str : Path where log file is to be generated.
        - img_fmt : str : Desired plot file extension.
    """
    set_logs_dir(logs_dir)
#     user_watch_impact = {}
    if not plot_dir:
        raise DefaultArgInvalidValError('INVALID_DEFAULT_ARG', '-p')
    if not img_fmt:
        raise DefaultArgInvalidValError('INVALID_DEFAULT_ARG', '-f')
    FLOG.debug('\n'.join(['Count: %s', 'Plot Dir: %s', 'Img Fmt: %s']) %
               (str(count), plot_dir, img_fmt))
    utils.empty_directory(plot_dir)
    if lang:
        lang = get_language(lang)
    CLOG.info('Lang: %s' % lang)
    user_watched_repo = high_profile_user_watch_events(lang, count)
    for user, watch_events in user_watched_repo.iteritems():
#         match = {'$match': {'payload.target.login': user}}
#         followers = Q.get_followers_count(FOLLOW_COLL, match)
        CLOG.info('User started - ' + user)
        for watch in watch_events:
            repo, event_created_at = watch['_id'], watch['created_at']
            fevent_created_at = utils.get_float_time(event_created_at)
            time_limit = \
                utils.get_24_hrs_hence_datetime_str(event_created_at)
            time_limit = time_limit.replace('-', '/') + ' '
            ftime_limit = utils.get_float_time(time_limit)

            match = {'repository.url': repo}
            if lang:
                match['repository.language'] = lang
            repo_all_events = Q.get_repo_watchers(gisc_msgs.ALL_COLL, match)
            x_tstamp, y_tstamp = get_growth(repo_all_events)
            x_pred, y_pred = get_predict(x_tstamp, y_tstamp, fevent_created_at)
            if is_eligible(y_tstamp, y_pred):
#                 user_impact =\
#                 get_set_user_impact_on_repos(
#                     user, followers, user_watched_repo, lang,
#                     user_watch_impact)
#                 continue
                plot_curve(plot_dir, user, repo, x_tstamp, y_tstamp,
                           fevent_created_at, ftime_limit, x_pred, y_pred,
                           lang, img_fmt)
                CLOG.info('\t Plotted -' + repo)


def setup_command_line_args_parse():
    """Setup the options for command line flags.

    :Returns:
        - ap : argparse.ArgumentParser object : Object with the options
        and their behaviour set.
    """
    _ap_args = dict(
        description=gisc_msgs.GISC_USAGE_MSGS['description'],
        argument_default=argparse.SUPPRESS, add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap = argparse.ArgumentParser(**_ap_args)
    # Usage help argument.
    ap.add_argument('-h', '--help', action='help',
                    help=gisc_msgs.GISC_USAGE_MSGS['help'])
    # Language argument.
    ap.add_argument('-l', nargs='?', dest='lang',
                    help=gisc_msgs.GISC_USAGE_MSGS['lang'])
    # Count argument.
    ap.add_argument('-c', nargs='?', dest='count', type=int,
                    help=gisc_msgs.GISC_USAGE_MSGS['count'])
    # Plot location argument.
    ap.add_argument('-p', nargs='?', dest='plot_dir',
                    default=gisc_msgs.PLOT_LOCATION,
                    help=gisc_msgs.GISC_USAGE_MSGS['plot_dir'])
    # Logs location argument.
    ap.add_argument('-m', nargs='?', dest='logs_dir',
                    help=gisc_msgs.GISC_USAGE_MSGS['logs_dir'])
    # Image extension argument.
    ap.add_argument('-f', nargs='?', dest='img_fmt', default=gisc_msgs.IMG_FMT,
                    help=gisc_msgs.GISC_USAGE_MSGS['img_fmt'])
    return ap


def get_ap_args(ap_obj, params=None):
    """Parse and get the command line arguments.

    :Parameters:
        - ap_obj : argparse.ArgumentParser object : Object with the
        options and their behaviour set.
        - params : list: Parameters to set options from. Used only in
        test cases. Hence, defaults to None.
    :Returns:
        - dict : Command line arguments.
    """
    # Group expected and garbage arguments.
    if params:
        ap_args, _ = ap_obj.parse_known_args(params)
    else:
        ap_args, _ = ap_obj.parse_known_args()
    return vars(ap_args)


if __name__ == '__main__':
    # Test users to eliminate complete process(for debug).
    _TEST_USERS = [u'jbourassa', u'jabennett86', u'paulmillr', u'markstory',
                   u'kakutani', u'marucc', u'iafonov', u'henrikpersson',
                   u'ingorenner', u'hmans']

    _args = get_ap_args(setup_command_line_args_parse())

    try:
        high_profile_user_watch_effect(**_args)
    except GISCError as e:
        CLOG.error(e.message)
