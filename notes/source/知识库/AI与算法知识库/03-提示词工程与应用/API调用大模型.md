## API调用大模型

### 1. 主流大模型的API的申请地址



#### **1.1 月之暗面 / Kimi chat**

> API key申请地址：https://platform.moonshot.cn/console/api-keys

> API文档地址：https://platform.moonshot.cn/docs

> API定价信息：https://platform.moonshot.cn/docs/price/chat



#### **1.2 百度 / 文心一言 **

先要申请Key，先要创建应用。登录百度智能云千帆控制台创建应用，创建成功后，在应用列表页获取AppID、API Key、Secret Key 等信息。

API key申请地址：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application

API文档地址：https://cloud.baidu.com/doc/WENXINWORKSHOP/s/flfmc9do2

API定价信息：https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Blfmc9dlf



#### **1.3 智谱 / GLM**

API key申请地址：https://bigmodel.cn/usercenter/apikeys

API文档地址：https://bigmodel.cn/dev/api

API定价信息：https://open.bigmodel.cn/pricing



#### **1.4 MiniMax**

API key申请地址：https://platform.minimaxi.com/user-center/basic-information/interface-key

API文档地址：https://platform.minimaxi.com/document/notice

API定价信息：https://platform.minimaxi.com/document/price



#### **1.5 阿里 / 通义千问 （Qwen）**

API key申请地址：https://dashscope.console.aliyun.com/apiKey

API文档地址：https://help.aliyun.com/zh/dashscope/developer-reference

API定价信息：https://dashscope.console.aliyun.com/billing



#### **1.6 科大讯飞 /讯飞星火 （Spark）**

跟百度文心一言一样，需要先创建应用（https://console.xfyun.cn/app/myapp），然后在应用里获取Key

API key申请地址：https://console.xfyun.cn/services/cbm

API文档地址：https://www.xfyun.cn/doc/spark/Web.html

API定价信息：https://xinghuo.xfyun.cn/sparkapi



#### **1.7 DeepSeek（深度求索）**

API key申请地址：https://platform.deepseek.com/api_keys

API文档地址：https://platform.deepseek.com/api-docs/zh-cn/

API定价信息：https://platform.deepseek.com/api-docs/zh-cn/pricing

---



### 2. Kimi Chat API申请与使用指南

**月之暗面科技有限公司**（Moonshot AI）开发的Kimi智能助手以其强大的语言理解和生成能力，成为了许多开发者和企业的首选工具。Kimi Chat API的开放，更是让这种能力得以在各种应用中灵活运用。本文将详细介绍如何申请和使用Kimi Chat API，帮助你快速上手并发挥其最大效用。

#### 2.1 准备工作

**1）注册Kimi账号**

首先，你需要访问Kimi开放平台的官方网站 [Moonshot AI](https://www.moonshot.cn/) 并注册一个账号。如果你已经拥有Kimi智能助手的账号，可以直接使用该账号登录。

**2） 登录Kimi开放平台**

使用你的Kimi账号登录Kimi开放平台。在平台的首页，你可以看到账户总览，包括平台赠送的体验额度。

**3） 创建API Key**

在开放平台的账户总览页面，点击创建API Key。创建完成后，系统会显示你的API Key。**请立即复制并保存**，因为API Key只会显示一次。



#### 2.2 API Key的使用

API Key是你调用Kimi Chat API的身份凭证，相当于你的账号密码。**不要泄露给他人**。使用API Key时，你可以通过以下几种方式进行认证：

**1）Bearer Token**

在调用API时，通过请求头携带API Key。例如，在Postman中新建一个POST请求，输入API地址 `https://api.moonshot.cn/v1/chat/completions`，在Authorization标签页选择“Bearer Token”方式，并在“Token”字段填入你的API Key。

**2）API Key参数**

在请求的URL中直接传递API Key。例如：

```
https://api.moonshot.cn/v1/chat/completions?api_key=你的API_Key
```



#### 2.3 API调用示例

**1）使用Postman测试API**

以Postman为例，进行API调用的测试：

- **新建POST请求**：在地址栏输入API地址 `https://api.moonshot.cn/v1/chat/completions`。

- **设置请求头**：进入Authorization标签页，选择“Bearer Token”方式，在“Token”字段填入你的API Key。

- **发送请求**：点击“Send”发出请求。稍等几秒钟，你应该能看到Kimi的回复。



**2）使用Python SDK**

如果你是Python开发者，可以使用OpenAI的Python SDK来调用Kimi Chat API。以下是示例代码：

```python
import openai

openai.api_key = "你的API_Key"

response = openai.ChatCompletion.create(
    model="moonshot-v1-8k",
    messages=[
        {"role": "user", "content": "你好，Kimi！"}
    ]
)

print(response)
```



#### 2.4 基本概念和进阶

**1）基本概念**

如果你是AI应用开发的新手，需要掌握一些基本概念，比如Kimi提供的模型、API的计费等。Kimi的API设计兼容行业标杆OpenAI，这意味着基于GPT API的项目可以无缝切换到Kimi API。

**2）Kimi的API设计**

Kimi在API设计方面兼容OpenAI，这意味着你可以享受到OpenAI开发生态的丰富资源。无论是后端工程师、前端工程师还是编程小白，都可以找到适合自己的上手路径。

**3）不同角色的上手路径**

- **后端工程师**：可以通过Kimi的官方API文档使用curl或OpenAI的Python SDK来调用API。
- **前端工程师**：可以通过开源项目学习使用Chat Completion API开发聊天机器人。
- **编程小白**：可以使用基于大模型API开发的工具，如智能体搭建平台、浏览器插件等，无需自己从零开发。



#### 2.5 Kimi Chat的特点

Kimi Chat不仅支持长文总结和生成、联网搜索、数据处理、编写代码、角色扮演和多语言翻译等功能，还支持多端同步，包括网页版、APP以及微信小程序。APP版还提供了个性化设置和离线功能，增强用户体验。



#### 2.6 小结

通过本文的介绍，你应该已经对如何申请和使用Kimi Chat API有了清晰的了解。无论是开发聊天机器人、进行数据分析还是编写代码，Kimi Chat API都能为你提供强大的支持。

---



### 3. 百度文心一言API申请与使用指南

> 百度文心一言是百度智能云推出的一款具有深度语义理解与生成能力的大语言模型。它广泛应用于文学创作、商业文案创作、数理逻辑推算等多个领域。本文将引导你如何一步步申请和使用文心一言API。

#### 3.1 准备工作

**1）注册百度智能云账号**

访问 [百度智能云官网](https://login.bce.baidu.com/new-reg?tpl=bceplat&from=portal) 进行注册，并完成实名认证。

**2）确保账户不欠费**

为保障服务稳定运行，请确保你的账户余额充足。



#### 3.2 申请预置模型

**1）登录控制台**

使用你的百度智能云账号登录 [百度智能云控制台](https://console.bce.baidu.com/qianfan/modelcenter/model/buildIn/list)。

**2）开通预置模型**

在控制台中，点击模型仓库下的“预置模型”，勾选需要的模型，新用户通常会有代金券赠送。



#### 3.3 创建应用

**1）应用接入**

在控制台中找到“应用接入”选项，点击进入。

**2）填写应用信息**

填写应用名称、描述等信息，并选择需要使用的模型。

**3）获取AppID、API Key和Secret Key**

应用创建成功后，系统会提供AppID、API Key和Secret Key，这些是调用API时的身份验证信息。



#### 3.4 获取接口访问凭证access_token

**1）准备API Key和Secret Key**

使用第3步中获取的API Key和Secret Key。

**2）获取access_token**

通过以下API调用获取access_token：

```bash
curl 'https://aip.baidubce.com/oauth/2.0/token?
grant_type=client_credentials&client_id=【API Key】&client_secret=【Secret Key】'
```

将上述命令中的`【API Key】`和`【Secret Key】`替换为你的实际值。

**3）使用access_token**

access_token是API调用的身份验证凭证，有效期默认为30天，注意在生产环境中及时刷新。



#### 3.5 在线调试（可选）

**1）使用在线调试工具**

在千帆平台上，利用在线调试工具对API进行测试和参数调整。

**2）调整参数**

根据需要调整temperature、top_p和penalty_score等参数，观察模型输出变化。



#### 3.6 调用API接口

**1）选择API接口**

根据需求选择相应的API接口，例如ERNIE-Bot。

**2）发起API调用**

使用获取的access_token进行API调用，可以通过编程语言如Python实现。



#### 3.7 编写代码示例（Python）

**1）获取access_token（Python示例）**

```python
import requests

def get_access_token():
    API_KEY = "你的API_Key"
    SECRET_KEY = "你的Secret_Key"
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    response = requests.get(url)
    return response.json()['access_token']

access_token = get_access_token()
print(access_token)
```

**2）调用文心一言API（Python示例）**

```python
def call_wenxin_api(message):
    headers = {
        'Content-Type': 'application/json'
    }
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token={access_token}"
    payload = {
        "messages": [{"role": "user", "content": message}]
    }
    response = requests.post(url, json=payload, headers=headers).json()
    return response

result = call_wenxin_api("你好，文心一言！")
print(result)
```



#### 3.8 注意事项

- 妥善保管API Key和Secret Key，避免泄露。

- 定期刷新access_token，尤其是在生产环境中。

- 根据实际需求选择合适的模型和参数。

  

> 通过上述步骤，你应该能够顺利地申请到文心一言API的使用权限，并将其集成到你的项目中。不断探索和实践，将帮助你更深入地了解和利用这一强大的AI工具。



### 4. 智谱GLM API申请与使用指南

智谱AI大模型，由清华智谱研发，提供了强大的语言处理能力，广泛应用于聊天机器人、文本生成、问答系统等场景。下面将手把手教你如何申请和使用智谱GLM API。

#### 4.1 准备工作

**1）访问智谱官网**

打开浏览器，访问智谱AI开放平台官网 [https://open.bigmodel.cn](https://open.bigmodel.cn/)。

**2）注册与登录**

在官网上注册账号，或使用已有账号登录。

**3）实名认证**

完成实名认证，可以选择个人身份证认证或公司营业执照认证。



#### 4.2 申请API Key

**1）访问API Keys页面**

实名认证完成后，访问用户中心的API Keys页面。

**2）创建API Key**

点击创建新的API Key，填写必要的信息，如应用名称等。

**3）记录API Key**

创建成功后，记录下API Key，这将作为后续API调用的身份验证凭证。



#### 4.3 安装SDK

**1）Python环境安装**

如果使用Python开发，通过以下命令安装SDK：

```bash
pip install zhipuai
```

**2）Java环境配置**

如果使用Java开发，需要在项目的`pom.xml`文件中添加相应的依赖：

```xml
<dependency>
    <groupId>cn.bigmodel.openapi</groupId>
    <artifactId>oapi-java-sdk</artifactId>
    <version>release-V4-2.0.2</version>
</dependency>
```



#### 4.4 编写客户端程序

**1）Python客户端示例**

使用Python编写客户端程序，调用GLM模型：

```python
from zhipuai import ZhipuAI

# 替换为你的API Key
client = ZhipuAI(api_key="你的APIKey")

response = client.chat.completions.create(
    model="glm-4",  # 指定模型名称
    messages=[
        {"role": "user", "content": "请输入你的问题或者需求"},
    ],
    stream=True,
)

for chunk in response:
    print(chunk.choices[0].delta)
```

**2. Java客户端示例**

请参考官方文档或社区提供的Java SDK使用示例



#### 4.5 测试API

**1）发起API调用**

使用编写的客户端程序，发起API调用，检查是否能够成功接收响应。

**2）检查返回结果**

检查API返回的结果是否符合预期，确保集成正确。



#### 4.6 注意事项

- API使用限制：注意API的免费调用次数有限，避免超出限额。

- 账户余额：定期检查账户余额，确保账户不欠费。

- 错误处理：遇到错误时，根据错误信息进行排查和处理。

- 文档与社区支持：充分利用官方文档和社区资源，解决开发中遇到的问题。

> 通过上述步骤，你已经掌握了如何申请和使用智谱GLM API。



### 5. MiniMax API申请与使用指南

MiniMax，作为一家专注于大模型研究的科技公司，推出了其先进的Assistants API，为开发者和企业提供了强大的自然语言处理能力。下面将为您提供一份详尽的MiniMax API申请与使用指南。



#### 5.1 了解MiniMax API

MiniMax Assistants API目前处于内测阶段，但已经向部分头部客户开放。这项服务以其高效率和出色的语言理解能力，被广泛应用于聊天机器人、内容创作、信息归纳总结等多个场景。



#### 5.2 申请内测资格

MiniMax Assistants API 是一项新兴的人工智能服务，目前处于内测阶段，并且已有一些头部客户开始使用这项服务。你需要在MiniMax的官网上申请内测资格。如果你是一名开发者或企业客户，可以通过官网提交申请。

**1）访问MiniMax官网**

打开浏览器，访问MiniMax的官方网站 https://www.minimaxi.com/。

**2）注册开发者账号**

在官网上找到注册入口，注册一个新的开发者账号。填写必要的信息，如邮箱、密码等。

**3）申请内测**

在注册完成后，根据官网提供的指引申请内测资格。通常需要填写一份内测申请表，描述你的使用场景和需求。

**4）等待审核**

提交申请后，耐心等待MiniMax团队的审核。审核通过后，你将收到内测资格的通知。



#### 5.3 创建和管理API密钥

**1）登录开发者控制台**

使用你的账号登录MiniMax开发者控制台。

**2）创建API密钥**

在控制台的“API管理”页面，点击“创建新密钥”按钮。系统将生成一个新的API密钥。

**3）保存API密钥**

请妥善保存生成的API密钥，因为它将用于后续的API调用验证。



#### 5.4 配置API使用

**1）添加支付信息**

在账户设置中添加支付信息，确保账户余额充足，以便于API服务的持续使用。

**2）设置API使用限制**

在“API配置”页面，根据需要设置API的使用限制，如请求频率限制、IP白名单等。



#### 5.5 编写客户端程序

**1）准备开发环境**

根据你的开发语言和环境，准备相应的开发工具和库。

**2）编写代码**

使用MiniMax提供的API文档和示例代码，编写客户端程序。以下是一个Python调用示例：

```python
import requests

# 替换为你的API密钥和GroupId
api_key = "你的API密钥"
group_id = "你的GroupId"
url = f"https://api.minimax.chat/v1/text/chatcompletion_v2"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

data = {
    "model": "abab5.5-chat",
    "messages": [
        # 根据需要添加对话内容
    ],
    # 其他参数
}

response = requests.post(url, headers=headers, json=data)
# 处理响应数据
```



#### 5.6 测试API调用

**1）发起API请求**

使用你的客户端程序，发起API请求，并检查是否能够成功接收响应。

**2）验证返回结果**

检查API返回的结果是否符合预期，确保集成正确。



#### 5.7 注意事项

- 妥善保管API密钥，避免泄露给未授权的人员。
- 定期检查账户余额，确保服务不中断。
- 遵循MiniMax API的使用条款和限制。



> 通过上述步骤，你已经掌握了如何申请和使用MiniMax Assistants API。请注意，具体的API调用细节和参数设置需要参考MiniMax官方文档，以确保正确使用API。同时，由于MiniMax Assistants API目前处于内测阶段，具体的申请流程和使用方法可能会有所变化



### 6. 阿里云通义千问API申请与使用指南

阿里云通义千问API是阿里云推出的一款基于超大规模语言模型的人工智能服务，它能够帮助开发者快速构建各种智能应用。下面将为您提供一份详尽的申请与使用指南。



#### 6.1 了解通义千问API

通义千问API基于阿里云自主研发的超大规模语言模型，具备强大的语言理解与生成能力，广泛应用于聊天机器人、内容创作、知识问答等场景。



#### 6.2 申请API Key

**1）注册阿里云账号**

如果您还没有阿里云账号，请先在[阿里云官网](https://www.aliyun.com/)注册。

**2）访问DashScope控制台**

登录阿里云账号后，访问[DashScope控制台](https://dashscope.console.aliyun.com/apiKey)。

**3）实名认证**

根据页面提示完成实名认证，这是获取API Key的前提条件。

**4）创建API Key**

在控制台中创建新的API Key，记录下生成的Key，它将作为后续API调用的身份验证凭证。



#### 6.3 安装DashScope SDK

**1）选择开发语言**

DashScope SDK支持Python和Java两种语言，根据您的开发需求选择相应的SDK。

**2）安装Python SDK**

如果使用Python开发，通过以下命令安装或更新SDK：

```bash
pip install dashscope --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**3）安装Java SDK**

如果使用Java开发，请根据官方文档指引安装Java SDK。



#### 6.4 配置API Key

**1）设置环境变量**

为安全起见，建议将API Key设置为环境变量，避免在代码中硬编码。

**2）配置示例**

以Python为例，您可以在`.env`文件中添加以下内容：

```plaintext
DASHSCOPE_API_KEY=您的API_Key
```



#### 6.5 编写客户端程序

**1）导入SDK**

根据开发语言导入相应的DashScope模块。

**2）编写调用代码**

使用申请到的API Key，编写客户端程序调用通义千问API。以下是Python和Java的示例代码：

- Python示例：

  ```python
  from http import HTTPStatus
  import dashscope
  def call_with_messages():
      messages = [
          {'role': 'system', 'content': 'You are a helpful assistant.'},
          {'role': 'user', 'content': '请介绍一下通义千问'}
      ]
      response = dashscope.Generation.call(
          dashscope.Generation.Models.qwen_turbo,
          messages=messages,
          result_format='message'
      )
      if response.status_code == HTTPStatus.OK:
          print(response)
      else:
          print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
              response.request_id, response.status_code,
              response.code, response.message
          ))
  if __name__ == '__main__':
      call_with_messages()
  ```

- Java示例：

  ```java
  import java.util.ArrayList;
  import java.util.List;
  // 其他导入...
  public class Main {
      public static void callWithMessage()
              throws NoApiKeyException, ApiException, InputRequiredException {
          Generation gen = new Generation();
          List<Message> messages = new ArrayList<>();
          Message systemMsg = Message.builder()
                  .role(Role.SYSTEM.getValue())
                  .content("You are a helpful assistant.")
                  .build();
          Message userMsg = Message.builder()
                  .role(Role.USER.getValue())
                  .content("请介绍一下通义千问")
                  .build();
          messages.add(systemMsg);
          messages.add(userMsg);
          GenerationParam param = GenerationParam.builder()
                  .model(Generation.Models.QWEN_TURBO)
                  .messages(messages)
                  .resultFormat(GenerationParam.ResultFormat.MESSAGE)
                  .build();
          GenerationResult result = gen.call(param);
          System.out.println(JsonUtils.toJson(result));
      }
      public static void main(String[] args){
          try {
              callWithMessage();
          } catch (ApiException | NoApiKeyException | InputRequiredException e) {
              System.out.println(e.getMessage());
          }
          System.exit(0);
      }
  }
  ```

这些示例展示了如何通过messages方式调用通义千问大模型。



#### 6.6 测试API调用

**1）运行客户端程序**

执行您的客户端程序，检查是否能够成功接收API响应。

**2）验证返回结果**

检查API返回的结果是否符合预期，确保集成正确。



#### 6.7 注意事项

- 妥善保管API Key，避免泄露给未授权的人员。
- 定期检查账户余额，确保服务不中断。
- 遵循通义千问API的使用条款和限制。



> 通过上述步骤，您已经掌握了如何申请和使用阿里云通义千问API。



### 7. 讯飞星火API申请与使用指南

科大讯飞作为国内领先的智能语音和人工智能企业，推出了讯飞星火API，为企业和开发者提供了强大的自然语言处理能力。下面将为您详细介绍如何申请和使用讯飞星火API。



#### 7.1 了解讯飞星火API

讯飞星火API基于科大讯飞自主研发的星火认知大模型，具备文本生成、语言理解、知识问答等能力，适用于各种智能应用场景，如聊天机器人、内容创作、知识库查询等。



#### 7.2 注册成为开发者

**1）访问讯飞开放平台**

打开浏览器，访问[讯飞开放平台](https://www.xfyun.cn/)。

**2）注册账号**

点击右上角的“注册”按钮，通过微信扫码、手机快捷登录或邮箱注册成为开发者。

**3）实名认证**

完成账号注册后，进行实名认证，这是使用API服务的前提条件。



#### 7.3 创建应用并获取API Key

**1）登录控制台**

使用您的账号登录讯飞开放平台控制台。

**2）创建应用**

在控制台中，点击“我的应用”创建一个新的应用，并填写应用名称和相关信息。

**3）获取AppID、API Secret和API Key**

应用创建成功后，您可以在应用详情页中找到AppID、API Secret和API Key，这些是API调用的身份验证信息。



#### 7.4 安装Python SDK

**1）环境要求**

确保您的Python环境版本为3.8或以上。

**2）安装命令**

在Python环境中执行以下命令安装讯飞星火API的SDK：

```bash
pip install xiaofeng-shenhuo -i https://pypi.tuna.tsinghua.edu.cn/simple
```



#### 7.5 编写客户端程序

**1）导入SDK**

在Python代码中导入讯飞星火API的SDK模块。

**2）使用API Key**

使用您在步骤3中获取的API Key进行API调用。

**3）示例代码**

以下是一个简单的Python客户端示例代码：

```python
from xiaofeng_shenhuo import SparkAPI

# 使用您的AppID、APISecret和APIKey进行初始化
api = SparkAPI(AppID='您的AppID', APISecret='您的APISecret', APIKey='您的APIKey')

# 调用API进行文本生成
response = api.text_generation("你好，世界！")

print(response)
```



#### 7.6 测试API调用

**1）运行客户端程序**

执行您的客户端程序，检查是否能够成功接收API响应。

**2）验证返回结果**

检查API返回的结果是否符合预期，确保集成正确。



#### 7.7 注意事项

- 妥善保管您的API Key，避免泄露给未授权的人员。
- 定期检查账户余额和API使用情况，确保服务不中断。
- 遵循讯飞星火API的使用条款和限制。



> 通过上述步骤，您已经掌握了如何申请和使用科大讯飞讯飞星火API。



### 8. DeepSeek API 申请与使用指南

DeepSeek API，一个兼容OpenAI API格式的强大工具，为开发者提供了丰富的自然语言处理能力。本文将为您展示如何申请和使用DeepSeek API，让您能够轻松集成智能对话补全功能。

#### 8.1 DeepSeek API概览

DeepSeek API基于先进的MoE模型，支持对话生成和补全，适用于聊天机器人、虚拟助手等应用场景。



#### 8.2 申请API Key

**1）注册DeepSeek平台账号**

访问[DeepSeek平台](https://platform.deepseek.com/)，注册并登录您的账号。

**2）创建API Key**

在用户中心或API管理页面，创建一个新的API Key。请妥善保管您的API Key，避免泄露。



#### 8.3 环境准备

**1）安装Python环境**

确保您的开发环境中已安装Python 3.8或以上版本。

**2）安装OpenAI SDK**

通过以下命令安装OpenAI的Python SDK：

```bash
pip3 install openai
```



#### 8.4 编写客户端程序

- 使用OpenAI SDK，您可以编写客户端程序来调用DeepSeek API。以下是一个使用Python的示例代码：

  ```python
  from openai import OpenAI
  
  # 请将 "<deepseek api key>" 替换为您的DeepSeek API Key
  client = OpenAI(api_key="<deepseek api key>", base_url="https://api.deepseek.com")
  response = client.chat.completions.create(
      model="deepseek-chat",
      messages=[
          {"role": "system", "content": "You are a helpful assistant"},
          {"role": "user", "content": "Hello"},
      ],
      stream=False  # 非流式输出，如果需要流式输出，设置为True
  )
  print(response.choices[0].message.content)
  ```

- 您也可以使用cURL命令行工具来发送请求，示例如下：

  ~~~bash
  curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -d '{
      "model": "deepseek-chat",
      "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
      ],
      "stream": false
  }'
  ``` [^43^]
  ~~~



#### 8.5 请求和响应处理

**1）解析响应**

API响应将返回JSON格式的数据，您可以根据需要解析并使用这些数据。

**2）错误处理**

如果遇到错误（如429或503），请根据错误信息进行相应处理，如稍后重试。



#### 8.6 流式输出

DeepSeek API支持流式输出，您可以设置`stream=True`来实时获取模型生成的文本。



#### 8.7 多轮对话实现

通过维护对话上下文，您可以使用DeepSeek API实现多轮对话功能。



#### 8.8 注意事项

- 请遵守DeepSeek API的使用条款和限制。
- 注意API Key的安全，避免在公共代码库中泄露。
- 监控API使用情况，确保不超过速率限制。



> 通过上述步骤，您已经了解了如何申请和使用DeepSeek API。