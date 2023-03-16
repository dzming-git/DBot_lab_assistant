# DBot_lab_assistant

DBot的实验课助手模块服务程序。

## 功能说明

该机器人目前支持以下功能：
- 登陆邮箱，下载学生发送的作业并分类归纳
- 自动监视邮箱，并下载作业

## 功能

#助教 指令 参数1 参数2 参数3 ......

---

### #连接邮箱

#### 功能说明

登录邮箱，该程序目前只支持IMAP协议登录

#### 参数说明

无参数。

---

### 下载附件

#### 功能说明

将未记录的，且满足命名要求的附件下载至指定文件夹

#### 参数说明

无参数。

---

### 自动下载

#### 功能说明

自动执行下载附件

#### 参数说明

参数为：”无“， 开始，start时，开始自动下载

参数为：停止，stop时，停止自动下载

---

## 安装运行

### 安装

1. 安装DBot微服务的平台程序 [DBot_platform](https://github.com/dzming-git/DBot_platform) 。

1. 安装DBot微服务的SDK [DBot_SDK](https://github.com/dzming-git/DBot_SDK)

2. 下载代码到本地的`DBot_monitor`目录。

3. 将`conf/authority`文件夹中`authority_sample.yaml`重命名为 `authority.yaml` ，配置用户权限。

4. 将`conf/experiment_info`文件夹中`experiment_info_sample.yaml`重命名为 `experiment_info.yaml`，配置相关参数。

5. 安装依赖库，运行以下命令：

   ``` python
   pip install -r requirements.txt
   ```

### 运行

1. 确保平台程序 [DBot_platform](https://github.com/dzming-git/DBot_platform)  正常运行，相关步骤可查询平台程序中的运行方法。

2. 运行监控服务程序 `app/server.py`：

   **注意 项目的工作目录必须是根目录**

   ``` python
   python -m app.server
   ```
   或者
   
   配置`run.bat`文件中运行该程序的python地址后，双击打开`run.bat`

## 配置文件

- `conf/experiment_info/experiment_info.yaml` - 配置文件，包括配置邮箱参数、作业文档名的正则表达式、保存地址、已处理邮件id的记录文件。
- `con/authority/authority.yaml` - 配置文件，包括用户权限信息。
- `conf/route_info/route_info.yaml` - 配置文件，包括机器人API网关、消息代理、该服务程序的配置信息。

## 授权许可

本项目使用 MIT 许可证，有关更多信息，请参阅 LICENSE 文件。

## 联系我们

如果您对本项目有任何问题或建议，请随时通过以下方式联系我们：

- Email: dzm_work@163.com
- QQ: 715558579
