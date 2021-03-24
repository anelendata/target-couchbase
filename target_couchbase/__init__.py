#!/usr/bin/env python3

import argparse, datetime, io, logging, re, sys, time, uuid
from collections import defaultdict
from tempfile import TemporaryFile

from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

import simplejson as json
import singer

from target_couchbase.schema import clean_and_validate

logger = singer.get_logger()


def get_or_create_collection(cluster, bucket_name, collection=None):
    bucket = cluster.bucket(bucket_name)
    if not collection:
        return bucket.default_collection()
    return bucket.collection(collection)


def is_batch_ready(batch):
    return len(batch) > 99


def flush_batch(cluster, bucket_name, batch, collection_name=None):
    collection = get_or_create_collection(cluster, bucket_name, collection_name)
    collection.upsert_multi(batch)


def write_records(cluster, username, password, bucket,
                  lines=None, collection_map=None, index_keys=None,
                  on_invalid_record="abort"):
    if on_invalid_record not in ("abort", "skip", "force"):
        raise ValueError("on_invalid_record must be one of" +
                         " (abort, skip, force)")

    state = None
    schemas = {}
    tables = {}
    key_properties = {}
    table_files = {}
    row_count = {}
    errors = {}

    cluster = Cluster("couchbase://" + cluster, ClusterOptions(
          PasswordAuthenticator(username, password)))

    count = 0
    invalids = 0
    current_batch = defaultdict(dict)

    for line in lines:
        try:
            message = singer.parse_message(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if isinstance(message, singer.RecordMessage):
            json_dumps = False
            record, invalids = clean_and_validate(message, schemas, invalids,
                                                  on_invalid_record, json_dumps)
            # python-couchbase does not like Decimal
            record_str = json.dumps(record)
            record = json.loads(record_str, use_decimal=False)

            if invalids == 0 or on_invalid_record == "force":
                record["_stream"] = message.stream
                collection_name = None
                if collection_map:
                    collection_name = collection_map.get(message.stream)
                if index_keys and index_keys.get(message.stream):
                    key = record[index_keys[message.stream]]
                else:
                    key = uuid.uuid4().hex

                current_batch[collection_name or "_"][key] = record

                if is_batch_ready(current_batch[collection_name or "_"]):
                    flush_batch(cluster, bucket, current_batch.pop(collection_name or "_"))

            row_count[message.stream] += 1
            state = None

        elif isinstance(message, singer.StateMessage):
            state = message.value
            # State may contain sensitive info. Not logging in production
            logger.debug("State: %s" % state)
            currently_syncing = state.get("currently_syncing")
            bookmarks = state.get("bookmarks")
            if currently_syncing and bookmarks:
                logger.info("State: currently_syncing %s - last_update: %s" %
                            (currently_syncing,
                             bookmarks.get(currently_syncing, dict()).get(
                                 "last_update")))

        elif isinstance(message, singer.SchemaMessage):
            table_name = message.stream

            if schemas.get(table_name):
                # Redundant schema rows
                continue

            schemas[table_name] = message.schema
            key_properties[table_name] = message.key_properties
            row_count[table_name] = 0
            errors[table_name] = None

        elif isinstance(message, singer.ActivateVersionMessage):
            # This is experimental and won't be used yet
            pass

        else:
            raise Exception("Unrecognized message {}".format(message))

        count = count + 1

    for collection_name, batch in current_batch.items():
        if batch:
            if collection_name == "_":
                collection_name = None
            flush_batch(cluster, bucket, batch, collection_name)

    return state


def _emit_state(state):
    if state is None:
        return
    line = json.dumps(state)
    logger.debug("Emitting state {}".format(line))
    sys.stdout.write("{}\n".format(line))
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file', required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    on_invalid_record = config.get('on_invalid_record', "abort")

    input_ = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    state = write_records(config["cluster"],
                          config["username"],
                          config["password"],
                          config["bucket"],
                          input_,
                          collection_map=config.get("collection_map"),
                          index_keys=config.get("index_keys"),
                          on_invalid_record=on_invalid_record)

    _emit_state(state)
    logger.debug("Exiting normally")

if __name__ == '__main__':
    main()
