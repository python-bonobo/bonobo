#! /bin/bash

__PATH__=$(cd $(dirname "$0")/..; pwd)
EXAMPLES=$(cd $__PATH__; find bonobo/examples -name \*.py -not -name _\*)

for example in $EXAMPLES; do
  echo "===== $example ====="
  (cd $__PATH__; time bonobo run $example > /dev/null);
done
