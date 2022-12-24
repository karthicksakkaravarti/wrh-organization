#! /bin/bash

inc_ver_type=patch
if [ -n "$1" ]; then
    inc_ver_type=$1
fi
old_version=$(node -p "require('./package.json').version");
version=$(npm version ${inc_ver_type})
echo "Building version [${version}] ..."
npm run build
if [ $? -ne 0 ]; then
  echo "Failed to build!";
  version=$(npm version ${old_version});
  exit 1;
fi

cd dist
git add -A
git commit -a -m "build ui version ${version}"

cd ..
git add -A
git commit -a
# git tag ${version}
echo "Built version [${version}] => OK"
