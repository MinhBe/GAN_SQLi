引用格式:罗艺铭,谭玉波,李建平.基于BERT-GAN 的SQL 注入攻击检测方法研究[J]. 微电子学与计算机,2024,41(11):39-
47.
LUO Y M,TAN Y B,LI J P. Research on SQL injection attacks detection method based on BERT-GAN[J]. Microelectronics &
Computer,2024,41(11):39-47.
DOI:10.19304/J.ISSN1000-7180.2023.0721
基于BERT-GAN 的SQL 注入攻击检测方法研究
罗艺铭,谭玉波,李建平
(河南工业大学 信息科学与工程学院, 河南 郑州 450001)
摘 要: 针对主流检测方法识别SQL 注入攻击面临的检测准确率不高和用于训练的大量真实数据集通常难以获
取的问题,提出了一种用于检测SQL 注入攻击的BERT-GAN 网络模型。通过半监督学习方案来综合对抗样本,
采用微调的BERT 模型处理未标记数据,利用生成对抗网络区分对抗性和真实示例以及检测恶意和良性样本。实
验结果表明,模型在公开管理和标准化数据集sqli,sqliv2 和自建的sqli-extend 数据集上与基于CNN、LSTM、BERT-
Base、GAN-Base 模型的SQL 注入攻击检测方法对比,准确率、精确率、召回率和F1 值均有一定程度提高。模型的
目标损失函数收敛速度更快说明所提模型具有高效性。
关键词: SQL 注入;攻击检测;生成对抗网络;BERT;半监督学习
中图分类号: TP393 文献标识码: A 文章编号: 1000-7180(2024)11-0039-09
Research on SQL injection attacks detection method based on BERT-GAN
LUO Yiming,TAN Yubo,LI Jianping
(College of Information science and Engineering, He'nan University of Technology, Zhengzhou 450001, China)
Abstract:A BERT-GAN network model for detecting SQL injection attacks is proposed to solve the problems faced by
the mainstream detection methods, such as low detection accuracy and difficult to obtain a large number of real data sets for
training. The confrontation samples are synthesized by a Semi-Supervised Learning scheme.The unmarked data is processed
using the fine-tuning of BERT-like architectures.Adversarial and real examples as well as detecting malicious and benign
samples are distinguished by generating confrontation settings. The experimental results demonstrate that the accuracy,
precision, recall and F1 score of the proposed model have been enhanced to a certain degree on openly managed and
standardized datasets such as sqli, sqliv2 and self-built sqli-extend datasets. These improvements are observed in
comparison to SQL injection detection methods based on CNN, LSTM, BERT-Base, and GAN-Base models. Furthermore,
the faster convergence rate of the target loss function indicates that the proposed model exhibits high efficiency.
Key words:SQL injection;attacks detection;generative adversarial network;BERT;semi-supervised learning

1 引言
近年来,随着移动互联网、物联网、5G 通信
等技术的快速发展,互联网与各行各业跨界融合。
不仅在消费及政企领域,网约车、网络支付、网络
购物、网络娱乐、网络新闻、在线办公、在线政务
等新兴应用改变了人们的生活和工作方式。而且在
生产及物流领域,5G+工业互联网形成了人、机、


收稿日期: 2023-09-13; 修回日期: 2023-11-12
基金项目:国家自然科学基金(62276091)

第 41 卷 第 11 期
微 电 子 学 与 计 算 机 https://www.journalmc.com
Vol. 41 No. 11
2024 年 11 月
MICROELECTRONICS & COMPUTER
November 2024
https://www.journalmc.com


---

物全面连接的新型生产方式,正在向航空航天、石
化化工、建材、港口、纺织、家电等垂直领域加速
延伸。支撑这些互联网应用及关键信息基础设施正
常运转的重要组件之一就是类型各异、分散部署的
数据库,储存着珍贵的行业数据及敏感的个人信息。
由于这些数据对网络黑色产业链有重大价值,因此
数据库一直是黑客攻击的重要目标。
2022 年3 月,NVIDIA 内部1TB 的敏感文件遭
窃,7 万员工信息泄露。同年11 月,社交软件脸书
(Facebook)被爱尔兰数据保护委员会因约5.33 亿用
户的个人数据被黑客窃取泄露,处以2.65 亿欧元
(合约20 亿人民币)的罚款。据统计,2022 年将近
20% 的中国网民遭遇过个人信息泄露事件
[1],在数
据安全领域,SQL 注入攻击一直是主要的威胁类型。
2020 年被确认的266 个数据库系统漏洞中,
MySQL 漏洞占据总漏洞数量的一半以上
[2]。此外,
在开源Web 应用程序安全项目 (Open Web Application Security Project, OWASP)中公布的10 个最常
见的应用程序漏洞中
[3],SQL 注入攻击的风险排在
第一位。因此,研究和防范SQL 注入攻击是一项必
要的安全任务。在此基础上,本文提出了一种基于
BERT-GAN 的SQL 注入攻击检测模型,以帮助软
件开发人员及时发现网络中可能存在的SQL 注入漏
洞,从而确保信息网络的安全。

2 研究背景

2.1 SQL 注入攻击原理
SQL 注入的概念第一次被提出在是1998 年
《Phrack》第54 期中的"NT Web Technology Vulnerabilities"文献里
[4],SQL 注入攻击的流程如图1
所示。攻击者不需要获取管理员的用户名和密码,
直接执行恶意SQL 命令欺骗服务器以访问资源,或
通过插入、修改以及删除数据篡改数据库
[5-8],导致
整个数据库的丢失或损坏。


浏览器
Web 服务器
数据库
SQL
注入攻击
选择查询
返回错误信息
返回数据
图1 SQL 注入攻击原理图
Fig. 1 Schematic diagram of SQL injection attack

新型的攻击与以往有很大不同,它可能会攻击
任何带有漏洞的动态ASP 页面,尤其是一些旧网
站
[9],攻击者可以使用HDSI、HBSI 等SQL 注入工
具直接攻击网站。这些工具的使用门槛很低,攻击
者很容易取得服务器的控制权,相应的防范难度和
造成的危害也提高了。

2.2 基于机器学习的注入攻击检测算法
机器学习检测算法通过提供的大量数据进行分
析并训练模型,具有灵活性和伸缩性
[10]。针对过多
的文本特征会产生"维灾难"及文本的训练和分类
时间过长等问题,文献[11] 使用支持向量机
(Support Vector Machine, SVM)作为分类器,提高
了检测SQL 注入攻击的召回率,降低了训练和分类
的时间开销。考虑到识别攻击的难度和成本,文
献[12] 使用了一种融合特征选择的随机森林(Random Forest, RF)的攻击检测方法,该方法集成了一
系列用于检测SQL 注入攻击的功能,通过分析
Web 访问日志来提取SQL 注入攻击特征,对异常
流量样本进行降维,将特征选择算法嵌入随机森林
的单个基学习器,提高了模型精度,然而这种方法
的准确性还有待提高。
为了进一步提升机器学习检测算法的性能,深
度学习检测算法学习了大量代表攻击或正常的历史
数据,识别攻击模式和了解检测到的流量,最终实
现在攻击发生之前预测将要产生的攻击。文献[13]
提出使用卷积神经网络(Convolutional Neural
Network, CNN)来检测PHP 代码中的SQL 注入漏洞,
通过定制预处理阶段来去除不必要的数据,添加语
义标签作为补充因素来提高训练效率。文献[14] 提
出一种基于长短期记忆网络(Long Short-Term Memory, LSTM)的SQL 注入攻击检测方法,生成有效的
正样本,解决了由于缺乏正样本而导致的过拟合问
题。但这些模型无法应对真实网络攻击的复杂环境,
尤其是存在对文本深层语义和挖掘上下文关联信息
方面的短板。

2.3 基于生成对抗网络的攻击检测算法
上述大多数的SQL 注入攻击检测算法过于强
调防御措施且难以识别新的攻击。传统的杀毒软件
用病毒库的方式,只能应付库中已存的病毒,往往
无法识别新产生的攻击,更何况要制定出相应的防
御策略。因此不能仅依靠挖掘现有的攻击报文来实
现攻击检测,而是要学习攻击者的理性决策过程,
尝试使用博弈的方式来理解攻击者和防御者之间的
对抗。
生成对抗网络 (Generative Adversarial Network,
GAN)
[15] 可以从文本中提取和学习细粒度信息,并
使用生成器创建合成示例,同时利用鉴别器来区分
40
微电子学与计算机
2024 年
https://www.journalmc.com


---

真实示例和合成示例,从而使生成器和鉴别器互相
对抗、共同进化。Yin 等
[16] 介绍了鉴别器并提出了
一个基于改进GAN 的网络检测的框架,以扩大标
签的数量,实现僵尸网络的识别和分类。Lee 等
[17]
提出一种使用GAN 创建相似攻击流量的方法,解
决真实网络攻击数据集的样本不平衡问题,通过增
强数据集来提高攻击检测的准确率。Lu 等
[18] 通过
将深度卷积GAN 与遗传算法相结合,在现有不同
类型的SQL 注入攻击样本的基础上生成新样本,增
加已知攻击样本的数目来缓解模型的过拟合。但这
些方法依赖先验知识的积累和生成的样本质量,难
以解决缺乏先验知识的新型SQL 注入攻击类型的样
本标签少的问题。
针对上述问题,本文继承了传统的SQL 注入
攻击检测算法的思想,试图采用深度学习方法,通
过结合GAN 模型博弈原理和基于上下文的BERT
模型,针对SQL 注入攻击检测不能及时检测到新
的SQL 注入攻击的问题,提出了基于BERT-GAN
的SQL 注入攻击检测模型。

3 基于BERT-GAN 的SQL 注入攻击检测
算法

3.1 算法模型整体架构
为了解决SQL 注入攻击检测框架需要根据已
知数据构建词库,采用语法解析、词嵌入编码可能
隐藏SQL 注入关键特征等问题,本文提出基于
BERT-GAN 的SQL 注入攻击检测模型,如图2 所
示。该模型使用基于上下文的BERT 模型,提供高
层次的样本特征向量,突出不同样本之间的差异;
同时为了实现特征的有效性并保持模型的泛化能力,
提出改进的半监督条件GAN 模型,生成器生成一
组给定随机分布的假示例向量,与未标记和标记样
本经由BERT 模型提取的特征向量分别作为鉴别器
的输入,利用对抗训练不断强化鉴别器,与此同时,
使用标记的数据来训练鉴别器进行分类,从而提高
模型的整体质量。该模型包括两个模块:数据特征
学习和异常检测。


数据特征学习模块
嵌入
无标签
有标签
编码器 1
编码器 2
BERT
编码器
解码器
生成器
鉴别器
真实
虚假
0
1
异常检测模块
随机噪声
编码器 N
图2 BERT-GAN 网络模型架构图
Fig. 2 BERT-GAN network model architecture diagram


3.2 数据特征学习
在实际场景中,大多数的基准测试都是在包含
数万个样本的数据集上实现的。然而,获得高质量
的注释数据是相当昂贵且耗时,相比之下,描述目
标任务特征的未标记示例通常较容易获取。而基于
Transformer 架构的双向编码器表示(Bidirectional
Encoder Representations from Transformers, BERT)是
基于上下文的嵌入模型
[19],有多层网络,每层包含
几个能够进行非线性变换的神经元,具有较强的非
线性拟合能力。为了减少对标注样例的需求,本文
的数据特征学习模块使用BERT 模型学习原始样本
的上下文表示,为异常检测模块提供高层次的样本
特征向量。
BERT 模型的核心由多个Transformer 编码器组
成,与传统的单向语言模型或者多个浅层拼接后的
单向语言模型相比, BERT 能够学到更重要的单词
或句子语义以及文本中不同级别的关系特征
[20],同
时使用上亿级别的无标注语料进行预训练,能够生
成更加准确、更通用的词向量或者句向量表示
[21]。
很多下游任务可以通过在预训练模型的基础上添加
第 11 期
罗艺铭,等:基于BERT-GAN 的SQL 注入攻击检测方法研究
41

https://www.journalmc.com
