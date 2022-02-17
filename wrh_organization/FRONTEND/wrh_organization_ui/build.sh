#! /bin/bash

inc_ver_type=patch
if [ -n "$1" ]; then
    inc_ver_type=$1
fi
version=$(npm version ${inc_ver_type})
echo "Building version [${version}] ..."
npm run build

cd dist
git add -A
git commit -a -m "build ui version ${version}"

cd ..
git add -A
git commit -a
# git tag ${version}
echo "Built version [${version}] => OK"
