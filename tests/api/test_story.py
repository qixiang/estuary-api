# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

from purview.models.koji import KojiBuild
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitCommit
from purview.models.errata import Advisory
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds


def test_get_stories(client):
    """Test getting a resource story from Neo4j with its relationships."""
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2017, 4, 26, 11, 44, 38),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
    })[0]
    advisory = Advisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-02',
        'content_types': ['docker'],
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '27825',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'product_short_name': 'RHEL',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'type_': 'RHBA',
        'update_date': datetime(2017, 8, 1, 7, 16),
        'updated_at': datetime(2017, 8, 1, 15, 43, 51)
    })[0]
    bug = BugzillaBug.get_or_create({
        'classification': 'Red Hat',
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'id_': '12345',
        'modified_time': datetime(2018, 2, 7, 19, 30, 47),
        'priority': 'high',
        'product_name': 'Red Hat Enterprise Linux',
        'product_version': '7.5',
        'resolution': '',
        'severity': 'low',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    })[0]
    build = KojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '2345',
        'name': 'slf4j',
        'release': '4.el7_4',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        "event_type_id": 8,
        "id_": "1180",
        "message_id": "ID:messaging-devops-broker01.test",
        "state": 2,
        "state_name": "COMPLETE",
        "state_reason": "All container images have been rebuilt.",
        "url": "/api/1/events/1180"
    })[0]
    cb = ContainerBuilds.get_or_create({
        "build_id": 15639047,
        "event_id": 1180,
        "id_": "397",
        "name": "jboss-eap-7-eap70-openshift-docker",
        "original_nvr": "jboss-eap-7-eap70-openshift-docker-1.4-36",
        "rebuilt_nvr": "jboss-eap-7-eap70-openshift-docker-1.4-36.1522094763",
        "state": 1,
        "state_name": "DONE",
        "state_reason": "Built successfully.",
        "time_completed": datetime(2017, 4, 2, 19, 39, 6),
        "time_submitted": datetime(2017, 4, 2, 19, 39, 6),
        "type_": 1,
        "type_name": "IMAGE",
        "url": "/api/1/builds/397"
    })[0]

    bug.resolved_by_commits.connect(commit)

    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)

    build.commits.connect(commit)
    build.advisories.connect(advisory)

    advisory.attached_builds.connect(build)
    advisory.triggers_freshmaker_event.connect(fm_event)

    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.triggers_container_builds.connect(cb)

    cb.triggered_by_freshmaker_event.connect(fm_event)

    expected = [['BugzillaBug',
                 [{'classification': 'Red Hat',
                   'creation_time': '2017-04-02T19:39:06+00:00',
                   'id': '12345',
                   'modified_time': '2018-02-07T19:30:47+00:00',
                   'priority': 'high',
                   'product_name': 'Red Hat Enterprise Linux',
                   'product_version': '7.5',
                   'resolution': '',
                   'severity': 'low',
                   'short_description': 'Some description',
                   'status': 'VERIFIED',
                   'target_milestone': 'rc',
                   'votes': 0}]],
                ['DistGitCommit',
                 [{'author_date': '2017-04-26T11:44:38+00:00',
                   'commit_date': '2017-04-26T11:44:38+00:00',
                   'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                   'log_message': 'Related: #12345 - fix xyz'}]],
                ['KojiBuild',
                 [{'completion_time': '2017-04-02T19:39:06+00:00',
                   'creation_time': '2017-04-02T19:39:06+00:00',
                   'epoch': '0',
                   'extra': None,
                   'id': '2345',
                   'name': 'slf4j',
                   'release': '4.el7_4',
                   'start_time': '2017-04-02T19:39:06+00:00',
                   'state': 1,
                   'version': '1.7.4'}]],
                ['Advisory',
                 [{'actual_ship_date': '2017-08-01T15:43:51+00:00',
                   'advisory_name': 'RHBA-2017:2251-02',
                   'content_types': ['docker'],
                   'created_at': '2017-04-03T14:47:23+00:00',
                   'id': '27825',
                   'issue_date': '2017-08-01T05:59:34+00:00',
                   'product_name': 'Red Hat Enterprise Linux',
                   'product_short_name': 'RHEL',
                   'release_date': None,
                   'security_impact': 'None',
                   'security_sla': None,
                   'state': 'SHIPPED_LIVE',
                   'status_time': '2017-08-01T15:43:51+00:00',
                   'synopsis': 'cifs-utils bug fix update',
                   'type': 'RHBA',
                   'update_date': '2017-08-01T07:16:00+00:00',
                   'updated_at': '2017-08-01T15:43:51+00:00'}]],
                ['FreshmakerEvent',
                 [{'event_type_id': 8,
                   'id': '1180',
                   'message_id': 'ID:messaging-devops-broker01.test',
                   'state': 2,
                   'state_name': 'COMPLETE',
                   'state_reason': 'All container images have been rebuilt.',
                   'url': '/api/1/events/1180'}]],
                ['ContainerBuilds',
                 [{'build_id': 15639047,
                   'dep_on': None,
                   'event_id': 1180,
                   'id': '397',
                   'name': 'jboss-eap-7-eap70-openshift-docker',
                   'original_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36',
                   'rebuilt_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36.1522094763',
                   'state': 1,
                   'state_name': 'DONE',
                   'state_reason': 'Built successfully.',
                   'time_completed': '2017-04-02T19:39:06+00:00',
                   'time_submitted': '2017-04-02T19:39:06+00:00',
                   'type': 1,
                   'type_name': 'IMAGE',
                   'url': '/api/1/builds/397'}]]]

    rv = client.get('/api/v1/story/bugzillabug/12345')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/distgitcommit/8a63adb248ba633e200067e1ad6dc61931727bad')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/kojibuild/2345')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/advisory/27825')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/freshmakerevent/1180')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/containerbuilds/397')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
