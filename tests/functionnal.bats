#!/usr/bin/env bats
# vim: set fileencoding=utf-8 filetype=bash 
#
#  Unit tests for function of renamePeopleTags.py
#
#

EXE=../renamePeopleTags.py

setup() {
    # Check environment
    [ -f "$EXE" -a -x "$EXE" ]
}

teardown() {
   :
}

@test "Collect shall be successfull" {
   rm -f people.yaml
   run "$EXE" collect -d in
   assert_success
   assert_file_equals expected/people.yaml people.yaml
}

@test "Rename shall be successfull" {
   cp in/empty.jpg out/empty.jpg
   rm -f renamed_people.yaml
   run "$EXE" rename -d out
   assert_success
   run "$EXE" collect -d out -o renamed_people.yaml
   assert_success
   assert_file_equals expected/renamed_people.yaml renamed_people.yaml
   if exiv2 pr -p a out/empty.jpg |grep -i " john"; then
      echo -E "out/empty.jpg should not contain any instance of John"
      return 1
   fi

}

load utils
