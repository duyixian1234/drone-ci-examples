# Drone CI

杜逸先 2021年12月15日

---

# 简介

> Drone is a self-service Continuous Integration platform for busy development teams.

[官网](https://www.drone.io/)
[文档](https://docs.drone.io/)
[Drone on duyixian.cn](http://drone.duyixian.cn)

---

# 特性

- 继承多种Git仓库（Github，Gitlab, Gitea等）
- 基于容器的运行时
- Pipeline as Code
- 分布式Runner
- 插件生态

---

# 核心概念

- Server
- Runner
- Pipeline

---

# Server 与 Runner

```yaml
version: '3'

services:
  drone-server:
    image: drone/drone:latest
    ports: ["9090:80"]
    restart: always
    volumes: ["/var/lib/drone:/data"]
    environment:
      DRONE_AGENTS_ENABLED: "true"
      DRONE_GITHUB_CLIENT_ID: ${DRONE_GITHUB_CLIENT_ID}
      DRONE_GITHUB_CLIENT_SECRET: ${DRONE_GITHUB_CLIENT_SECRET}
      DRONE_RPC_SECRET: ${DRONE_RPC_SECRET}
      DRONE_SERVER_HOST: ${SERVER_HOST}
      DRONE_SERVER_PROTO: http
  drone-runner:
    image: drone/drone-runner-docker:1
    ports: ["3000:3000"]
    volumes: ["/var/run/docker.sock:/var/run/docker.sock"]
    environment:
      DRONE_RPC_PROTO: http
      DRONE_RPC_HOST: ${SERVER_HOST}
      DRONE_RPC_SECRET: ${DRONE_RPC_SECRET}
      DRONE_RUNNER_CAPACITY: 3
```
---

# 本地运行

[安装drone-cli](https://docs.drone.io/quickstart/cli/)

```bash
drone exec .drome.yml
```

---

# Pipeline

使用Yaml格式定义的CI流水线

```yaml
kind: pipeline
type: docker
name: default

steps:
- name: greeting
  image: busybox
  commands:
  - echo "Hello World"
```

---
## 触发条件

- 可以设置流水线的触发条件
- [包括分支、事件、定时任务等多种触发条件](https://docs.drone.io/pipeline/docker/syntax/trigger/)

---

## 多步骤流水线

同一流水线的不同步骤共用同一个工作目录。

```yaml
kind: pipeline
type: docker
name: default

steps:
- name: Step 1
  image: busybox
  commands:
  - echo "Step 1"
  - echo "Hello World" > a.txt
- name: Step 2
  image: busybox
  commands:
  - echo "Step 2"
  - cat a.txt
- name: Step 3
  image: busybox
  commands:
  - echo "Step 3"
  - rm a.txt
```
---

## 并行步骤

- 默认每一个步骤在前一个步骤运行结束后开始。
- 可以通过`depends_on`属性设置每一个步骤的依赖，定义一个有向无环图。

```yaml
steps:
- name: Prepare
  image: busybox
  commands: ["echo "Hello World" > a.txt", "echo "Hello World" > b.txt"]
- name: Slow Step A
  depends_on: ["Prepare"]
  image: busybox
  commands: ["sleep 5", "cat a.txt > c.txt"]
- name: Slow Step B
  depends_on: ["Prepare"]
  image: busybox
  commands: ["sleep 10", "cat b.txt"]
- name: Slow Step C
  depends_on: ["Slow Step A"]
  image: busybox
  commands: ["sleep 5", "cat c.txt"]
- name: Cleanup
  depends_on: ["Slow Step B", "Slow Step C"]
  image: busybox
  commands: ["rm a.txt b.txt c.txt"]
```
---

## Python后端CI流水线

```yaml
kind: pipeline
type: docker
name: default

steps:
- name: CI
  image: python:3.9-slim
  commands:
  - cd 04-python-example
  - pip install -r requirements-dev.txt -q
  - pylint main.py
  - mypy main.py
  - isort --check main.py
  - pytest tests --cov=main --cov-fail-under=80
```

---

## 前端CI流水线

```yaml
steps:
- name: Install Dependencies
  image: node:16-alpine
  commands:
  - cd 05-frontend-example
  - npm install --quiet --registry=http://mirrors.cloud.tencent.com/npm/
- name: Run Tests
  depends_on:
  - Install Dependencies
  image: node:16-alpine
  commands:
  - cd 05-frontend-example
  - npm run test --watchAll=false
- name: Build
  depends_on:
  - Install Dependencies
  image: node:16-alpine
  commands:
  - cd 05-frontend-example
  - npm run build
```
---

## 集成测试（运行后台服务）

可以定义后台运行的服务

```yaml
kind: pipeline
type: docker
name: default

steps:
- name: Prepeare
  image: redis
  commands:
  - while ! redis-cli -h cache ping; do sleep 1; done
  - echo "Cache server is up"
- name: Run Integration Tests
  image: python:3.9-slim
  commands:
  - cd 06-integration-test
  - pip install -r requirements-dev.txt -q
  - pytest -sv test_cache.py

services:
- name: cache
  image: redis
```

---

## 自定义克隆

- 可以指定克隆深度
- 可以通过submodules步骤克隆子模块

```yaml
clone:
  depth: 1
steps:
- name: submodules
  image: alpine/git
  commands:
  - 'git config --global url."https://github.com/".insteadOf git@github.com:'
  - git submodule update --init --recursive
- name: api-server
  detach: true
  image: python:3.8-slim
  commands:
  - cd qr-web
  - pip install -r requirements.txt -q
  - flask run --host 0.0.0.0 --port 8080
- name: Test API
  image: curlimages/curl
  commands:
  - while ! curl -s -o /dev/null http://api-server:8080/status; do sleep 1; done
  - rm -rf ./qr.png
  - curl http://api-server:8080/qr?content=Hello%20World
```

---

## 使用插件

[插件市场](http://plugins.drone.io/)
Drone CI的插件实际上就是一个容器，可以像定义不同步骤一样使用插件

```yaml
kind: pipeline
name: default

steps:
- name: download  
  image: plugins/download
  settings:
    source: https://raw.githubusercontent.com/duyixian1234/drone-ci-examples/master/README.md
- name: cat
  image: busybox
  commands:
  - cat README.md
```

---



# 配置仓库

- 可以在web端单独配置每一个仓库的CI设置
- *注意*：Project Visibility最好设置为Private或者Internal，设置为Public的项目为所有人可见。
- 可以自定义使用的流水线文件

<img src="https://s2.loli.net/2021/12/15/XzFmTZK16RAQorU.jpg" style="width:75%" class="rounded shadow" />

---

## 配置Secrets

- 可以将一些敏感信息配置为Secrets(例如发布Token, 消息机器人Token)
- *注意* 谨慎设置“Allow Pull Requests”选项，攻击者可能会通过PR窃取你的私密信息

<img src="https://s2.loli.net/2021/12/15/6ieapn8SOJD1RBk.png"  style="width:50%" class="rounded shadow" >

---

## 使用Secrets

- 可以在step中将Secrets注入为环境变量

```yaml
 - name: notify
    image: lddsb/drone-dingtalk-message
    settings:
      token:
        from_secret: dingtalk
      type: markdown
      message_color: true
      message_pic: true
      sha_link: true
    when:
      status: [success, failure]
```
---
# The End

感谢观看