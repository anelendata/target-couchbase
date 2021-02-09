# target-couchbase

![target-couchbase](https://raw.githubusercontent.com/anelendata/target-couchbase/master/assets/target-couchbase.png)

## What is it

This is a [Singer](https://singer.io) target that loads JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md)
to [Couchbase Server](https://docs.couchbase.com/home/server.html).

## Install

First, make sure Python 3.6 or higher is installed on your system or follow
these  installation instructions for Mac or Ubuntu.

```
pip install -U couchbase
pip install -U target-couchbase
```

Or you can install the lastest development version from GitHub:

```
pip install -U couchbase
pip install --no-cache-dir https://github.com/anelendata/target-couchbase/archive/master.tar.gz#egg=target-couchbase
```
Note: Please refer to
[Couchbase documentation](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html)
for the details of installation of couchbase Python SDK.

## Run

### Step 1: Configure

Create a file called target_config.json in your working directory, following
this sample:

```
{
    "cluster": "{{ your-couchbase-server.com }}:8091",
    "username": "{{ couchbase_username }}",
    "password": "{{ couchbase_password }}",
    "bucket": "{{ your-bucket-name }}"
}
```

### Step 2: Run

target-bigquery can be run with any Singer Target. As example, let use
[tap-exchangeratesapi](https://github.com/singer-io/tap-exchangeratesapi).

```
pip install tap-exchangeratesapi
```

And create tap_config.json that looks like:

```
{
    "base": "USD",
    "start_date": "2021-01-11"
}
```
(Adjust your start date. 7 days ago is recommended for the test)

Run:

```
tap-exchangeratesapi -c tap_config.json | target-couchbase -c target_config.json
```

## Original repository

- https://github.com/anelendata/target-couchbase

# About this project

This project is developed by
ANELEN and friends. Please check out the ANELEN's
[open innovation philosophy and other projects](https://anelen.co/open-source.html)

![ANELEN](https://avatars.githubusercontent.com/u/13533307?s=400&u=a0d24a7330d55ce6db695c5572faf8f490c63898&v=4)
---

Copyright &copy; 2021~ Anelen Co., LLC
