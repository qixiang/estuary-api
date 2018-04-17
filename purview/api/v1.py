# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import collections
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound

from purview import version
from purview.utils.general import str_to_bool, get_neo4j_node, create_query, query_neo4j
from purview.models import story_flow
from neomodel import UniqueIdProperty


api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/about')
def about():
    """
    Display general information about the app.

    :rtype: flask.Response
    """
    return jsonify({'version': version})


@api_v1.route('/<resource>/<uid>')
def get_resource(resource, uid):
    """
    Get a resource from Neo4j.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    # Default the relationship flag to True
    relationship = True
    if request.args.get('relationship'):
        relationship = str_to_bool(request.args['relationship'])

    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    if relationship:
        return jsonify(item.serialized_all)
    else:
        return jsonify(item.serialized)


@api_v1.route('/story/<resource>/<uid>')
def get_resource_story(resource, uid):
    """
    Get the story of a resource from Neo4j.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    for prop_def in item.defined_properties().values():
        if isinstance(prop_def, UniqueIdProperty):
            forward_query = create_query(item, prop_def.name, uid)
            backward_query = create_query(item, prop_def.name, uid, reverse=True)
            break

    results_unordered = {}
    if forward_query:
        results_unordered = query_neo4j(forward_query)

    if backward_query:
        results_unordered.update(query_neo4j(backward_query))

    results = collections.OrderedDict()
    curr_label = 'BugzillaBug'
    while curr_label:
        if curr_label in results_unordered:
            results[curr_label] = results_unordered[curr_label]

        curr_label = story_flow[curr_label]['forward_label']

    return jsonify(list(results.items()) or item)
