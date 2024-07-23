package eventsservice

import rego.v1

default allow := false

allow if {
	input.method == "GET"
	input.path[0] == "api"
}

allow if {
	some role in input.roles
	input.method == "POST"
	input.path[0] == "api"
	role == "admin"
}

allow if {
	some role in input.roles
	input.method == "DELETE"
	input.path[0] == "api"
	role == "admin"
}
