@[TOC](目录)

## Minikube 搭建
### 1、安装
```shell
# 可选代理 https://gh-proxy.com/  https://ghproxy.net/
curl -LO https://gh-proxy.com//https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```
### 2、启动
```shell
指定 Calico 作为 CNI：要不最新版本 kindnet 会有兼容问题
minikube start --image-mirror-country='cn' --cni=calico
```
### 3、交互测试
```shell
minikube kubectl -- get pods -A
```
### 4、拉取启动dashboard
```shell
minikube dashboard
# minikube kubectl -- describe pod -n kubernetes-dashboard kubernetes-dashboard-6df74558bd-ldng6
# minikube kubectl -- describe pod -n kubernetes-dashboard dashboard-metrics-scraper-69cbd87b98-4mnmn
# 自动拉取会失败，根据错误日志拉取相关的镜像
docker pull kubernetesui/dashboard:v2.7.0
docker pull kubernetesui/metrics-scraper:v1.0.8
# 用完整的名称重新打标签
docker tag kubernetesui/dashboard:v2.7.0 docker.io/kubernetesui/dashboard:v2.7.0
docker tag kubernetesui/metrics-scraper:v1.0.8 docker.io/kubernetesui/metrics-scraper:v1.0.8
# 将镜像保存为 tar 包
docker save kubernetesui/dashboard:v2.7.0 -o dashboard.tar
docker save kubernetesui/metrics-scraper:v1.0.8 -o metrics-scraper.tar
# 加载到 Minikube 内部
minikube image load dashboard.tar
minikube image load metrics-scraper.tar
rm dashboard.tar metrics-scraper.tar

minikube kubectl -- delete pods -n kubernetes-dashboard --all
# 如果还不行，那应该是里面认证的版本号@sha256: 摘要 也需要对上，所以可以直接把 @sha256:...这些第一删除
# 改 imagePullPolicy: Never
minikube kubectl -- edit deployment -n kubernetes-dashboard kubernetes-dashboard
minikube kubectl -- edit deployment -n kubernetes-dashboard dashboard-metrics-scraper
minikube kubectl -- delete pods -n kubernetes-dashboard --all
```
### 5、访问dashboard
```shell
# 方法一：手动指定转发，访问地址 http://localhost:8080
minikube kubectl -- port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8080:80 --address='0.0.0.0'
# 当然也可以放在后台
nohup minikube kubectl -- port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8080:80 --address='0.0.0.0' > /dev/null 2>&1 &

# 方法二：自动转发， 访问地址随机生成
minikube service kubernetes-dashboard -n kubernetes-dashboard --url
```
### 6、版本查询（满足 >= v1.30）
```shell
minikube version
minikube version: v1.39.0
```