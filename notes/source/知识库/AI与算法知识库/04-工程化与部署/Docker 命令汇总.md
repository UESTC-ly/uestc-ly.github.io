# Docker 命令汇总

Docker 是一个开源的应用容器引擎，它允许开发者打包他们的应用以及应用的运行环境到一个可移植的容器中。以下是一些常用的 Docker 命令：

**1. docker build** - 根据 Dockerfile 构建镜像。

- 例如：`docker build -t myimage .`

**2. docker run** - 运行一个容器实例。

- 例如：`docker run -d -p 4000:80 myimage`

**3. docker ps** - 列出当前正在运行的容器。

- 例如：`docker ps`

**4. docker stop** - 停止一个或多个正在运行的容器。

- 例如：`docker stop container_id`

**5. docker start** - 启动一个或多个之前停止的容器。

- 例如：`docker start container_id`

**6. docker restart** - 重启一个或多个容器。

- 例如：`docker restart container_id`

**7. docker rm** - 删除一个或多个容器。

- 例如：`docker rm container_id`

**8. docker rmi** - 删除一个或多个镜像。

- 例如：`docker rmi image_id`

**9. docker images** - 列出本地的镜像。

- 例如：`docker images`

**10. docker pull** - 从远程仓库拉取一个镜像或仓库。

- 例如：`docker pull myimage`

**11. docker push** - 将一个镜像或仓库推送到远程仓库。

- 例如：`docker push myimage`

**12. docker logs** - 获取容器的日志输出。

- 例如：`docker logs container_id`

**13. docker exec** - 在运行的容器中执行命令。

- 例如：`docker exec -it container_id /bin/bash`

**14. docker network** - 管理 Docker 网络。

- 例如：`docker network ls`

**15. docker volume** - 管理 Docker 数据卷。

- 例如：`docker volume create`

**16. docker-compose** - 管理多容器 Docker 应用。

- 例如：使用 `docker-compose up` 来启动服务。

**17. docker attach** - 附加到一个正在运行的容器的stdin、stdout和stderr。

- 例如：`docker attach container_id`

**18. docker cp** - 在本地文件系统和Docker容器之间复制文件或文件夹。

- 例如：`docker cp container_id:/path/to/container/file /path/to/local/file`

**19. docker commit** - 从容器创建一个新的镜像。

- 例如：`docker commit container_id mynewimage`

**20. docker diff** - 检查容器文件系统的更改。

- 例如：`docker diff container_id`

**21. docker inspect** - 显示一个或多个容器或镜像的详细信息。

- 例如：`docker inspect container_id`

**22. docker load** - 从一个tar归档文件中加载一个镜像。

- 例如：`docker load < image.tar`

**23. docker save** - 将一个或多个镜像保存到一个tar归档文件中。

- 例如：`docker save -o image.tar myimage`

**24. docker tag** - 给镜像添加一个新的标签。

- 例如：`docker tag myimage myimage:tagname`

**25. docker top** - 显示容器内运行的进程。

- 例如：`docker top container_id`

**26. docker stats** - 显示容器的资源使用情况。

- 例如：`docker stats`

**27. docker prune** - 清理不再使用的资源，如悬空的镜像、停止的容器、未使用的网络和数据卷。

- 例如：`docker system prune`

**28. docker login** - 登录到一个Docker注册中心。

- 例如：`docker login`

**29. docker logout** - 从Docker注册中心登出。

- 例如：`docker logout`

**30. docker search** - 在Docker Hub上搜索镜像。

- 例如：`docker search myimage`

**31. docker create** - 创建一个新的容器，但不启动它。

- 例如：`docker create -p 4000:80 myimage`

**32. docker rename** - 重命名一个容器。

- 例如：`docker rename old_name new_name`

**33. docker update** - 更新容器的配置。

- 例如：`docker update --cpus 2 container_id`

**34. docker info** - 显示Docker守护进程的详细信息。

- 例如：`docker info`

**35. docker version** - 显示Docker的版本信息。

- 例如：`docker version`

**36. docker system** - 管理Docker守护进程的资源，如网络、镜像、容器和卷。

- 例如：`docker system df`

**37. docker port** - 列出容器的端口映射情况。

- 例如：`docker port container_id`

**38. docker logs -f** - 跟随容器的日志输出，实时显示日志。

- 例如：`docker logs -f container_id`

**39. docker build --no-cache** - 构建镜像时不使用缓存。

- 例如：`docker build --no-cache -t myimage .`

**40. docker run --rm** - 容器退出时自动清理容器文件系统。

- 例如：`docker run --rm -it ubuntu bash`

**41. docker run --entrypoint** - 覆盖容器的默认入口点。

- 例如：`docker run --entrypoint /bin/bash myimage`

**42. docker run --name** - 给容器指定一个名称。

- 例如：`docker run --name mycontainer -d myimage`

**43. docker run --network** - 指定容器连接的网络。

- 例如：`docker run --network mynet myimage`

**44. docker run --add-host** - 添加一个自定义的主机名到容器的 /etc/hosts 文件中。

- 例如：`docker run --add-host myhost:192.168.1.1 myimage`

**45. docker run --cap-add** - 向容器添加Linux能力。

- 例如：`docker run --cap-add SYS_ADMIN myimage`

**46. docker run --security-opt** - 设置容器的安全选项。

- 例如：`docker run --security-opt seccomp=unconfined myimage`

**47. docker run --read-only** - 将容器的根文件系统设置为只读。

- 例如：`docker run --read-only myimage`

**48. docker run --tmpfs** - 挂载一个临时文件系统到容器。

- 例如：`docker run --tmpfs /run myimage`

**49. docker run --volumes-from** - 从另一个容器挂载数据卷。

- 例如：`docker run --volumes-from othercontainer myimage`

**50. docker run --ulimit** - 设置Linux ulimit 配置。

- 例如：`docker run --ulimit nofile=1024:1024 myimage`

**51. docker run --device** - 给容器添加设备。

- 例如：`docker run --device /dev/snd myimage`

**52. docker run --sysctl** - 设置容器的内核参数。

- 例如：`docker run --sysctl net.ipv4.ip_forward=1 myimage`

**53. docker run --oom-kill-disable** - 禁用容器的OOM（内存不足）杀死。

- 例如：`docker run --oom-kill-disable myimage`

**54. docker run --oom-score-adj** - 设置容器的OOM评分调整值。

- 例如：`docker run --oom-score-adj=500 myimage`

**55. docker stats --all** - 显示所有容器的资源使用情况，包括停止的容器。

- 例如：`docker stats --all`

**56. docker network create** - 创建一个新的网络。

- 例如：`docker network create mynet`

**57. docker network connect** - 将容器连接到一个网络。

- 例如：`docker network connect mynet container_id`

**58. docker network disconnect** - 将容器从网络断开。

- 例如：`docker network disconnect mynet container_id`

**59. docker network rm** - 删除一个网络。

- 例如：`docker network rm mynet`

**60. docker volume create --name** - 创建并命名一个新的数据卷。

- 例如：`docker volume create --name myvolume`

**61. docker volume ls** - 列出所有的数据卷。

- 例如：`docker volume ls`

**62. docker volume inspect** - 显示数据卷的详细信息。

- 例如：`docker volume inspect myvolume`

**63. docker volume rm** - 删除一个数据卷。

- 例如：`docker volume rm myvolume`