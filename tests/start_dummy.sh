#! /usr/bin/sh

start_dummy() {
	curl -X POST http://localhost:8000/fuzzers/start \
			-H "Content-Type: application/json" \
			-d '{"campaign_id":"test_campaign","fuzzer_type":"dummy","config":{}}'
}
