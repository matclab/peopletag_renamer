# vim: set fileencoding=utf-8 filetype=bash 
#
# utility functions for tests
#

assert_success() {
    if [[ $status -ne 0 ]]; then
	echo "Command exited with status code $status"
	show_output
	return 1
    fi
}

assert_failure() {
    if [[ $status -eq 0 ]]; then
	echo "Command should have failed"
	show_output
	return 1
    fi
}

show_output() {
    echo "Output is:"
    echo -E "$output" | sed 's/^/  /'
}

assert_file_equals() {
    diff $1 $2
}
