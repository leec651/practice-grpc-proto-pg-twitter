#!/usr/bin/env bash

# remove previously generated proto python files
rm -f protos/*.py

# generate the definition file
python -m grpc_tools.protoc -I . \
--grpc_python_out=. \
./tweet.proto ./user.proto

# generate the type file
python -m grpc_tools.protoc -I . \
--python_out=.  \
./tweet_types.proto ./user_types.proto