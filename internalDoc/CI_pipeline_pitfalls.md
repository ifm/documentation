# GitLab CI CD pipeline pitfalls

## example for release pipeline for ROS
```
image: gcc:latest

stages:
  - build

copy content to GH:
  stage: build
  tags:
    - shared_docker
  variables:
    GIT_SUBMODULE_STRATEGY: recursive
  before_script:
  script:
    - git config --global user.email "support.robotics@ifm.com"
    - git config --global user.name "ifm-csr"

    # get GH branch 
    - git clone -b v1.0.x https://${ROS1MIRROR}:x-oauth-basic@github.com/ifm/ifm3d-ros.git repo
    - cd repo
    - rm -r *

    # copy changes
    - cp -r ${CI_PROJECT_DIR}/CHANGELOG.rst .
    - cp -r ${CI_PROJECT_DIR}/.clang-format .
    - cp -r ${CI_PROJECT_DIR}/LICENSE .
    - cp -r ${CI_PROJECT_DIR}/README.md . 
    - cp -r ${CI_PROJECT_DIR}/ifm3d-ros .
    - cp -r ${CI_PROJECT_DIR}/ifm3d_ros_driver .
    - cp -r ${CI_PROJECT_DIR}/ifm3d_ros_msgs .
    - cp -r ${CI_PROJECT_DIR}/ifm3d_ros_driver .

    # add changes
    - git add -A
    - git commit -m "add latest dev changes and fixes" --allow-empty
    # push changes
    - git push 

    # # test mirror repo
    # - git clone --bare https://github.com/exampleuser/old-repository.git
    # - cd old-repository.git 
    # - git push --mirror https://github.com/exampleuser/new-repository.git

  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_REF_NAME != $CI_DEFAULT_BRANCH
```

## personal access tokens
+ Pushing to GH requires you to create a personal access token on GH:
    + `click on you avatar -> settings -> developer settings ->personal access tokens`
    + the token name is ambiguous and will not be required anymore
    + copy the token to your clipboard
    + The user who will push has to have elevated rights on GH: 
        + ADMIN rights work but are discouraged because they introduce unnecessary risks  
        + Maintainer rights: are the way to go. `settings -> manage access -> select the user` SET: ROLE write


+ Go to your gitlab.dev.ifm project of choice and add the access token to your project of choice:
    + In the lefthand bar you should see the menu item: settings. If you don't see it get maintainer rights for this repo.
    + `settings -> CI/CD -> Variables -> add variable`
    + Remember the `variable` name. This name will be needed in your CI pipeline for authenticating to the GH repo.  
    See the `${ROS1MIRROR} in the example above. Replace this with your variable name.