#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

from platform import python_version

import pytest

from elastic_transport import __version__
from elastic_transport.client_utils import (
    client_meta_version,
    create_user_agent,
    parse_cloud_id,
)


def test_create_user_agent():
    assert create_user_agent(
        "enterprise-search-python", "7.10.0"
    ) == "enterprise-search-python/7.10.0 (Python/{}; elastic-transport/{})".format(
        python_version(),
        __version__,
    )


@pytest.mark.parametrize(
    ["version", "meta_version"],
    [
        ("7.10.0", "7.10.0"),
        ("7.10.0-alpha1", "7.10.0p"),
        ("3.9.0b1", "3.9.0p"),
        ("3.9.pre1", "3.9p"),
    ],
)
def test_client_meta_version(version, meta_version):
    assert client_meta_version(version) == meta_version


def test_parse_cloud_id():
    cloud_id = parse_cloud_id(
        "cluster:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ0ZmE4ODIxZTc1NjM0MDMyYmVk"
        "MWNmMjIxMTBlMmY5NyQ0ZmE4ODIxZTc1NjM0MDMyYmVkMWNmMjIxMTBlMmY5Ng=="
    )
    assert cloud_id.cluster_name == "cluster"
    assert cloud_id.es_address == (
        "4fa8821e75634032bed1cf22110e2f97.us-east-1.aws.found.io",
        443,
    )
    assert cloud_id.kibana_address == (
        "4fa8821e75634032bed1cf22110e2f96.us-east-1.aws.found.io",
        443,
    )


@pytest.mark.parametrize(
    ["cloud_id", "port"],
    [
        (
            ":dXMtZWFzdC0xLmF3cy5mb3VuZC5pbzo5MjQzJDRmYTg4MjFlNzU2MzQwMzJiZ"
            "WQxY2YyMjExMGUyZjk3JDRmYTg4MjFlNzU2MzQwMzJiZWQxY2YyMjExMGUyZjk2",
            9243,
        ),
        (
            ":dXMtZWFzdC0xLmF3cy5mb3VuZC5pbzo0NDMkNGZhODgyMWU3NTYzNDAzMmJlZD"
            "FjZjIyMTEwZTJmOTckNGZhODgyMWU3NTYzNDAzMmJlZDFjZjIyMTEwZTJmOTY=",
            443,
        ),
    ],
)
def test_parse_cloud_id_ports(cloud_id, port):
    cloud_id = parse_cloud_id(cloud_id)
    assert cloud_id.cluster_name == ""
    assert cloud_id.es_address == (
        "4fa8821e75634032bed1cf22110e2f97.us-east-1.aws.found.io",
        port,
    )
    assert cloud_id.kibana_address == (
        "4fa8821e75634032bed1cf22110e2f96.us-east-1.aws.found.io",
        port,
    )


@pytest.mark.parametrize(
    "cloud_id",
    [
        "cluster:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ0ZmE4ODIxZTc1NjM0MDMyYmVkMWNmMjIxMTBlMmY5NyQ=",
        "cluster:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ0ZmE4ODIxZTc1NjM0MDMyYmVkMWNmMjIxMTBlMmY5Nw==",
    ],
)
def test_parse_cloud_id_no_kibana(cloud_id):
    cloud_id = parse_cloud_id(cloud_id)
    assert cloud_id.cluster_name == "cluster"
    assert cloud_id.es_address == (
        "4fa8821e75634032bed1cf22110e2f97.us-east-1.aws.found.io",
        443,
    )
    assert cloud_id.kibana_address is None


@pytest.mark.parametrize(
    "cloud_id",
    [
        "cluster:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbzo0NDMkJA==",
        "cluster:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbzo0NDM=",
    ],
)
def test_parse_cloud_id_no_es(cloud_id):
    cloud_id = parse_cloud_id(cloud_id)
    assert cloud_id.cluster_name == "cluster"
    assert cloud_id.es_address is None
    assert cloud_id.kibana_address is None


@pytest.mark.parametrize(
    "cloud_id",
    [
        "cluster:",
        "dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQ0ZmE4ODIxZTc1NjM0MDMyYmVkMWNmMjIxMTBlMmY5NyQ=",
        "cluster:ā",
    ],
)
def test_invalid_cloud_id(cloud_id):
    with pytest.raises(ValueError) as e:
        parse_cloud_id(cloud_id)
    assert str(e.value) == "Cloud ID is not properly formatted"
